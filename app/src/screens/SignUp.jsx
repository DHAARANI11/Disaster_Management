import { useLayoutEffect, useState } from "react"
import { 
	Keyboard,
	KeyboardAvoidingView,
	SafeAreaView, 
	Text, 
	View, 
	TouchableWithoutFeedback, 
	ScrollView
} from "react-native"
import Input from "../common/Input"
import Button from "../common/Button"
import api from "../core/api"
import utils from "../core/utils"
import useGlobal from "../core/global"
import COLORS from "../assets/colors"


function SignUpScreen({ navigation }) {
	const [username,  setUsername]  = useState('')
	const [firstName, setFirstName] = useState('')
	const [lastName,  setLastName]  = useState('')
	const [email, setEmail] = useState('')
	const [phone_no,  setPhone_no]  = useState('')
	const [adhaar_no, setAdhaar_no] = useState('')
	const [address, setAddress] = useState('')
	const [pincode, setPincode] = useState('')
	const [organization_name, setOrganization_name] = useState('')
	const [profession, setProfession] = useState('')
	const [organization_address, setOrganization_address] = useState('')
	const [lattitude, setLattitude] = useState('')
	const [longitude, setLongitude] = useState('')
	const [location, setLocation] = useState('')
	const [Org_pincode, setOrg_Pincode] = useState('')
	const [password1, setPassword1] = useState('')
	const [password2, setPassword2] = useState('')

	const [usernameError,  setUsernameError]  = useState('')
	const [firstNameError, setFirstNameError] = useState('')
	const [lastNameError,  setLastNameError]  = useState('')
	const [emailError, setEmailError] = useState('')
	const [phone_noError,  setPhone_noError]  = useState('')
	const [adhaar_noError, setAdhaar_noError] = useState('')
	const [addressError, setAddressError] = useState('')
	const [pincodeError, setPincodeError] = useState('')
	const [organization_nameError, setOrganization_nameError] = useState('')
	const [professionError, setProfessionError] = useState('')
	const [organization_addressError, setOrganization_addressError] = useState('')
	const [lattitudeError, setLattitudeError] = useState('')
	const [longitudeError, setLongitudeError] = useState('')
	const [locationError, setLocationError] = useState('')
	const [Org_pincodeError, setOrg_PincodeError] = useState('')
	const [password1Error, setPassword1Error] = useState('')
	const [password2Error, setPassword2Error] = useState('')

	const login = useGlobal(state => state.login)

	useLayoutEffect(() => {
		navigation.setOptions({
			headerShown: false
		})
	}, [])

	function onSignUp() {
		// Check username
		const failUsername = !username || username.length < 5
		if (failUsername) {
			setUsernameError('Username must be >= 5 characters')
		}
		// Check firstName
		const failFirstName = !firstName
		if (failFirstName) {
			setFirstNameError('First Name was not provided')
		}
		// Check last Name
		const failLastName = !lastName
		if (failLastName) {
			setLastNameError('Last Name was not provided')
		}
		const failEmail = !email
		if (failEmail) {
			setEmailError('Email was not provided')
		}
		
		// Check last Name
		const failPhone_no = !phone_no
		if (failPhone_no) {
			setPhone_noError('phone number was not provided')
		}
		const failAdhaar_no = !adhaar_no
		if (failAdhaar_no) {
			setAdhaar_noError('Aadhar number was not provided')
		}
		const failAddress = !address
		if (failAddress) {
			setAddressError('Address was not provided')
		}
        const failPincode = !pincode 
		if (failPincode) {
			setPincodeError('pincode was not provided')
		}
		const failOrganization_name = !organization_name
		if (failOrganization_name) {
			setOrganization_nameError('Organization name was not provided')
		}
		const failProfession= !profession
		if (failProfession) {
			setProfessionError('Organization type was not provided')
		}
		const failOrganization_address = !organization_address
		if (failOrganization_address) {
			setOrganization_addressError('Organization address was not provided')
		}
		const failLattitude = !lattitude
		if (failLattitude) {
			setLattitudeError('location was not provided')
		}
		const failLongitude = !longitude
		if (failLongitude) {
			setLongitudeError('location was not provided')
		}
		const failLocation = !location
		if (failLocation) {
			setLocationError('location was not provided')
		}
		const failOrg_Pincode= !Org_pincode
		if (failOrg_Pincode) {
			setOrg_PincodeError('Organization pincode was not provided')
		}
		// Check password1
		const failPassword1 = !password1 || password1 < 8
		if (failPassword1) {
			setPassword1Error('Password is too short')
		}
		// Check password2
		const failPassword2 = password1 !== password2
		if (failPassword2) {
			setPassword2Error('Passwords don\'t match')
		}
		// Break out of the fucntion if there were any issues
		if (failUsername ||
				failFirstName ||
				failLastName ||
				failEmail ||
			    failPhone_no ||
			    failAdhaar_no ||
			    failAddress||
			    failPincode||
			    failOrganization_name||
			    failProfession||
			    failOrganization_address||
				failLattitude||
				failLongitude||
			    failLocation||
			    failOrg_Pincode||
				failPassword1 ||
				failPassword2) {
			return
		}

		// Make signin request
		api({
			method: 'POST',
			url: '/chat/signup/',
			data: {
				username: username,
				first_name: firstName,
				last_name: lastName,
				email:email,
				phone_no:phone_no,
				adhaar_no:adhaar_no,
				address:address,
				pincode:pincode,
				organization_name:organization_name,
				profession:profession,
				organization_address:organization_address,
				lattitude:lattitude,
				longitude:longitude,
				location:location,
				Org_pincode:Org_pincode,
				password: password1
			}
		})
		.then(response => {
			utils.log('Sign Up:', response.data)
			
			const credentials = {
				username: username,
				password: password1
			}
			login(
				credentials,
				response.data.user,
				response.data.tokens
			)
		})
		.catch(error => {
			if (error.response) {
				console.log(error.response.data);
				console.log(error.response.status);
				console.log(error.response.headers);
			} else if (error.request) {
				console.log(error.request);
			} else {
				console.log('Error', error.message);
			}
			console.log(error.config);
		})
	}

	return (
		<SafeAreaView style={{ flex: 1, backgroundColor: COLORS.white }}>
			<KeyboardAvoidingView behavior="height" style={{ flex: 1 }}>
			<ScrollView style={ {flex: 1}}>
				<TouchableWithoutFeedback onPress={Keyboard.dismiss}>
					<View style={{ flex: 1, justifyContent: 'center', paddingHorizontal: 16 }}>

					<Text style={{
                        fontSize: 22,
                        fontWeight: 'bold',
                        marginVertical: 12,
                        color: COLORS.black
                    }}>
                        Create Account
                    </Text>

					<Text style={{
                        fontSize: 16,
                        color: COLORS.black
                    }}>Connect with your team!!</Text>


						<Input 
							title='Username' 
							value={username}
							error={usernameError}
							setValue={setUsername}
							setError={setUsernameError}
						/>

						<Input 
							title='First Name'
							value={firstName}
							error={firstNameError}
							setValue={setFirstName}
							setError={setFirstNameError}
						/>

						<Input 
							title='Last Name'
							value={lastName}
							error={lastNameError}
							setValue={setLastName}
							setError={setLastNameError}
						/>

                        <Input 
							title='Email'
							value={email}
							error={emailError}
							setValue={setEmail}
							setError={setEmailError}
						/>
						
						<Input 
							title='phone number'
							value={phone_no}
							error={phone_noError}
							setValue={setPhone_no}
							setError={setPhone_noError}
						/>

						<Input 
							title='Aadhar number'
							value={adhaar_no}
							error={adhaar_noError}
							setValue={setAdhaar_no}
							setError={setAdhaar_noError}
						/>
						<Input 
							title='Address'
							value={address}
							error={addressError}
							setValue={setAddress}
							setError={setAddressError}
						/>
						<Input 
							title='pincode'
							value={pincode}
							error={pincodeError}
							setValue={setPincode}
							setError={setPincodeError}
						/>
						<Input 
							title='Organization Name'
							value={organization_name}
							error={organization_nameError}
							setValue={setOrganization_name}
							setError={setOrganization_nameError}
						/>
						<Input 
							title='Profession'
							value={profession}
							error={professionError}
							setValue={setProfession}
							setError={setProfessionError}
						/>
						<Input 
							title='Organization Address'
							value={organization_address}
							error={organization_addressError}
							setValue={setOrganization_address}
							setError={setOrganization_addressError}
						/>
						<Input 
							title='Organization lattitude'
							value={lattitude}
							error={lattitudeError}
							setValue={setLattitude}
							setError={setLattitudeError}
						/>
						<Input 
							title='Organization longitude'
							value={longitude}
							error={longitudeError}
							setValue={setLongitude}
							setError={setLongitudeError}
						/>
						<Input 
							title='Organization location'
							value={location}
							error={locationError}
							setValue={setLocation}
							setError={setLocationError}
						/>
						<Input 
							title='Organization Pincode'
							value={Org_pincode}
							error={Org_pincodeError}
							setValue={setOrg_Pincode}
							setError={setOrg_PincodeError}
						/>
						
						<Input 
							title='Password'
							value={password1}
							error={password1Error}
							setValue={setPassword1}
							setError={setPassword1Error}
							secureTextEntry={true}
						/>

						<Input 
							title='Retype Password'
							value={password2}
							error={password2Error}
							setValue={setPassword2}
							setError={setPassword2Error}
							secureTextEntry={true}
						/>

						<Button title='Register' onPress={onSignUp} />

						<Text style={{ textAlign: 'center', marginTop: 40 }}>
							Already have an account? <Text 
								style={{ color: 'blue' }}
								onPress={() => navigation.goBack()}
							>
								Sign in
							</Text>
						</Text>


					</View>
				</TouchableWithoutFeedback>
				</ScrollView>
			</KeyboardAvoidingView>
		</SafeAreaView>
	)
}

export default SignUpScreen