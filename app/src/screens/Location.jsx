import React from 'react'
import { WebView } from 'react-native-webview'
import { View, StyleSheet } from 'react-native'
import useGlobal from '../core/global'

const LocationScreen = () => {
  const user=useGlobal(state=>state.user)
  const url = `https://www.google.com/maps?q=${user.longitude}`
  return (
    <View style={styles.container}>
      <WebView
        source={{
          uri: url
        }}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 100
  }
});

export default LocationScreen
