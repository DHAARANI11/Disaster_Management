import { create } from 'zustand'
import secure from './secure'
import api, { ADDRESS } from './api'
import utils from './utils'

//   Socket receive message handlers

function responseFriendList(set, get, friendList) {
	set((state) => ({
		friendList: friendList
	}))
}

function responseTeamList(set, get, TeamList) {
	set((state) => ({
		TeamList: TeamList
	}))
}

function responseFriendNew(set, get, friend) {
	const friendList = [friend, ...get().friendList]
	set((state) => ({
		friendList: friendList
	}))
}


function responseMessageList(set, get, data) {
	set((state) => ({
		messagesList: [...get().messagesList, ...data.messages],
		messagesNext: data.next,
		messagesUsername: data.friend.username
	}))
}


function responseMessageSend(set, get, data) {
	const username = data.friend.username
	// Move friendList item for this friend to the start of 
	// list, update the preview text and update the time stamp
	const friendList = [...get().friendList]
	const friendIndex = friendList.findIndex(
		item => item.friend.username === username
	)
	if (friendIndex >= 0) {
		const item = friendList[friendIndex]
		item.preview = data.message.text
		item.updated = data.message.created
		friendList.splice(friendIndex, 1)
		friendList.unshift(item)
		set((state) => ({
			friendList: friendList
		}))
	}
	// If the message data does not belong to this friend then 
	// dont update the message list, as a fresh messageList will 
	// be loaded the next time the user opens the correct chat window
	if (username !== get().messagesUsername) {
		return
	}
	const messagesList = [data.message, ...get().messagesList]
	set((state) => ({
		messagesList: messagesList,
		messagesTyping: null
	}))
}



function responseMessageType(set, get, data) {
	if (data.username !== get().messagesUsername) return
	set((state) => ({
		messagesTyping: new Date()
	}))
}




function responseRequestAccept(set, get, connection) {
	const user = get().user
	// If I was the one that accepted the request, remove 
	// request from the  requestList
	if (user.username === connection.receiver.username) {
		const requestList = [...get().requestList]
		const requestIndex = requestList.findIndex(
			request => request.id === connection.id
		)
		if (requestIndex >= 0) {
			requestList.splice(requestIndex, 1)
			set((state) => ({
				requestList: requestList
			}))
		}
	} 
	// If the corresponding user is contained within the  
	// searchList for the  acceptor or the  acceptee, update 
	// the state of the searchlist item
	const sl = get().searchList
	if (sl === null) {
		return
	}
	const searchList = [...sl]

	let  searchIndex = -1
	// If this user  accepted
	if (user.username === connection.receiver.username) {
		searchIndex = searchList.findIndex(
			user => user.username === connection.sender.username
		)
	// If the other user accepted
	} else {
		searchIndex = searchList.findIndex(
			user => user.username === connection.receiver.username
		)
	}
	if (searchIndex >= 0) {
		searchList[searchIndex].status = 'connected'
		set((state) => ({
			searchList: searchList
		}))
	}
}


function responseRequestConnect(set, get, connection) {
	const user = get().user
	// If i was the one that made the connect request, 
	// update the search list row
	if (user.username === connection.sender.username) {
		const searchList = [...get().searchList]
		const searchIndex = searchList.findIndex(
			request => request.username === connection.receiver.username
		)
		if (searchIndex >= 0) {
			searchList[searchIndex].status = 'pending-them'
			set((state) => ({
				searchList: searchList
			}))
		}
	// If they were the one  that sent the connect 
	// request, add request to request list
	} else {
		const requestList = [...get().requestList]
		const requestIndex = requestList.findIndex(
			request => request.sender.username === connection.sender.username
		)
		if (requestIndex === -1) {
			requestList.unshift(connection)
			set((state) => ({
				requestList: requestList
			}))
		}
	}
}


function responseRequestList(set, get, requestList) {
	set((state) => ({
		requestList: requestList
	}))
}


function responseSearch(set, get, data) {
	set((state) => ({
		searchList: data
	}))
}


function responseThumbnail(set, get, data) {
	set((state) => ({
		user: data
	}))
}




const useGlobal = create((set, get) => ({


	//   Initialization

	initialized: false,

	init: async () => {
		const credentials = await secure.get('credentials')
		if (credentials) {
			try {
				const response = await api({
					method: 'POST',
					url: '/chat/signin/',
					data: {
						username: credentials.username,
						password: credentials.password
					}
				})
				if (response.status !== 200) {
					throw 'Authentication error'
				}
				const user = response.data.user
				const tokens = response.data.tokens

				secure.set('tokens', tokens)

				set((state) => ({
					initialized: true,
					authenticated: true,
					user: user
				}))
				return
			} catch (error) {
				console.log('useGlobal.init: ', error)
			}
		}
		set((state) => ({
			initialized: true,
		}))
	},
  
	//   Authentication

	authenticated: false,
	user: {},

	login: (credentials, user, tokens) => {
		secure.set('credentials', credentials)
		secure.set('tokens', tokens)
		set((state) => ({
			authenticated: true,
			user: user
		}))
	},

	logout: () => {
		secure.wipe()
		set((state) => ({
			authenticated: false,
			user: {}
		}))
	},


	//edit

	authenticated: false,
  user: {},
  editProfile: async (updatedProfileData) => {
    try {
      // Get the stored credentials from secure storage
      const credentials = await secure.get('credentials');

      if (!credentials) {
        console.error('Credentials not found');
        return;
      }

      // Perform an API call to update the user's profile on the server
      const response = await api({
        method: 'PUT',
        url: '/chat/signup/',
        data: {
          username: credentials.username,
          password: credentials.password,
          // Include any other fields you want to update
          ...updatedProfileData,
        },
      });

      if (response.ok) {
        // If the API call is successful, update the local state
        set((state) => ({
          user: {
            ...state.user,
            // Update user data with the new information
            // You might receive this data in the API response or use the updatedProfileData directly
            ...updatedProfileData,
          },
        }));

        // Optionally, you can perform any additional actions after a successful edit
        console.log('Profile edited successfully');
      } else {
        // Handle errors if the API call fails
        console.error('Failed to edit profile:', response.statusText);
      }
    } catch (error) {
      console.error('Error during profile edit:', error);
    }
  },

	//     Websocket

	socket: null,

	socketConnect: async () => {
		const tokens = await secure.get('tokens')

		const url = `ws://${ADDRESS}/chat/?token=${tokens.access}`

		const socket = new WebSocket(url)
		socket.onopen = () => {
			utils.log('socket.onopen')

			socket.send(JSON.stringify({
				source: 'request.list'
			}))
			socket.send(JSON.stringify({
				source: 'friend.list'
			}))
			socket.send(JSON.stringify({
				source: 'team.list'
			}))
		}
		socket.onmessage = (event) => {
			// Convert data to javascript object
			const parsed = JSON.parse(event.data)

			// Debug log formatted  data
			utils.log('onmessage:', parsed)

			const responses = {
				'friend.list':     responseFriendList,
				'friend.new':      responseFriendNew,
				'message.list':    responseMessageList,
				'message.send':    responseMessageSend,
				'message.type':    responseMessageType,
				'request.accept':  responseRequestAccept,
				'request.connect': responseRequestConnect,
				'request.list':    responseRequestList,
				'search':          responseSearch,
				'thumbnail':       responseThumbnail,
				'team.list':       responseTeamList,
			}
			const resp = responses[parsed.source]
			if (!resp) {
				utils.log('parsed.source "' + parsed.source + '" not found')
				return
			}
			// Call response function
			resp(set, get, parsed.data)
		}
		socket.onerror = (e) => {
			utils.log('socket.onerror', e.message)
		}
		socket.onclose = () => {
			utils.log('socket.onclose')
		}
		set((state) => ({
			socket: socket
		}))
	},

	socketClose: () => {
		const socket =  get().socket
		if (socket) {
			socket.close()
		}
		set((state) => ({
			socket: null
		}))
	},

	//     Search

	searchList: null,

	searchUsers: (query) => {
		if (query) {
			const socket = get().socket
			socket.send(JSON.stringify({
				source: 'search',
				query: query
			}))
		} else {
			set((state) => ({
				searchList: null
			}))
		}
	},

	//team
	TeamList:null,

	//     Requests

	friendList: null,

	//     Messages

	messagesList: [],
	messagesNext: null,
	messagesTyping: null,
	messagesUsername: null,

	messageList: (connectionId, page=0) => {
		if (page === 0) {
			set((state) => ({
				messagesList: [],
				messagesNext: null,
				messagesTyping: null,
				messagesUsername: null
			}))
		} else {
			set((state) => ({
				messagesNext: null
			}))
		}
		const socket = get().socket
		socket.send(JSON.stringify({
			source: 'message.list',
			connectionId: connectionId,
			page: page
		}))
	},

	messageSend: (connectionId, message) => {
		const socket = get().socket
		socket.send(JSON.stringify({
			source: 'message.send',
			connectionId: connectionId,
			message: message
		}))
	},

	messageType: (username) => {
		const socket = get().socket
		socket.send(JSON.stringify({
			source: 'message.type',
			username: username
		}))
	},



	//     Requests

	requestList: null,

	requestAccept: (username) => {
		const socket = get().socket
		socket.send(JSON.stringify({
			source: 'request.accept',
			username: username
		}))
	},

	requestConnect: (username) => {
		const socket = get().socket
		socket.send(JSON.stringify({
			source: 'request.connect',
			username: username
		}))
	},

	//     Thumbnail

	uploadThumbnail: (file) => {
		const socket = get().socket
		socket.send(JSON.stringify({
			source: 'thumbnail',
			base64: file.base64,
			filename: file.fileName
		}))
	}

}))




export default useGlobal