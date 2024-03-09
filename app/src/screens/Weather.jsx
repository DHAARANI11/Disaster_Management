import React, { useEffect, useState } from 'react'
import { View, Text, ScrollView, StyleSheet } from 'react-native'
import apiKey from '../core/config'
import useGlobal from '../core/global'

const WeatherReport = ({ location }) => {
  const [weatherData, setWeatherData] = useState(null);
  const [earthquakeAlert, setEarthquakeAlert] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getWeatherData = async () => {
      const weatherstackUrl = `http://api.weatherstack.com/current?access_key=${apiKey}&query=${location}`;
      try {
        const weatherResponse = await fetch(weatherstackUrl);
        const weatherData = await weatherResponse.json();

        if ('current' in weatherData) {
          const weather = weatherData.current;
          setWeatherData(weather);

          const abnormalConditions = ["storm", "tornado", "heavy rain"];
          const hasAbnormalConditions = abnormalConditions.some(keyword =>
            weather.weather_descriptions[0].toLowerCase().includes(keyword)
          );
          setEarthquakeAlert(hasAbnormalConditions);

        } else {
          setError(`Error: Unable to retrieve weather data for ${location}`);
        }
      } catch (error) {
        setError(`An error occurred: ${error.message}`);
      }
    };

    getWeatherData();
  }, [location, apiKey]);

  if (error) {
    return <Text>{error}</Text>;
  }

  if (!weatherData) {
    return <Text>Loading...</Text>;
  }

  return (
    <View>    
      <Text
      style={{
        fontWeight: 'bold',
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:20
        
    }}>
        {`Weather report for ${location}:`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:30
        
    }}>{`Temperature: ${weatherData.temperature}°C`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:40
        
    }}
      >{`Description: ${weatherData.weather_descriptions[0]}`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:50
        
    }}>{`Humidity: ${weatherData.humidity}%`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:60
        
    }}>{`Wind Speed: ${weatherData.wind_speed} km/h`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:70
        
    }}>{`Wind Direction: ${weatherData.wind_direction}`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:80
        
    }}>{`Atmospheric Pressure: ${weatherData.pressure} hPa`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:90
        
    }}>{`UV Index: ${weatherData.uv_index}`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:100
        
    }}>{`Visibility: ${weatherData.visibility} km`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:110
        
    }}>{`Cloud Cover: ${weatherData.cloud_cover}%`}</Text>
      <Text
      style={{
        textAlign: 'left',
        color: '#303030',
        fontSize: 20,
        top:120
        
    }}>{`Sunrise: ${weatherData.sunrise}`}</Text>

      {earthquakeAlert && <Text>Earthquake alert: There are recent earthquakes in the area.</Text>}
    </View>
  )
}

const statesInTamilNadu = [
    'Ariyalur',
    'Chennai',
    'Coimbatore',
    'Cuddalore',
    'Dharmapuri',
    'Dindigul',
    'Erode',
    'Kanchipuram',
    'Kanyakumari',
    'Karur',
    'Krishnagiri',
    'Madurai',
    'Nagapattinam',
    'Namakkal',
    'Perambalur',
    'Pudukkottai',
    'Ramanathapuram',
    'Salem',
    'Sivagangai',
    'Thanjavur',
    'Theni',
    'Thiruvallur',
    'Thiruvarur',
    'Thoothukudi',
    'Tiruchirappalli',
    'Tirunelveli',
    'Tiruppur',
    'Trichy',
    'Tuticorin',
    'Vellore',
    'Villupuram',
    'Virudhunagar',

];


const WeatherScreen = () => {
    return (
      <ScrollView contentContainerStyle={styles.scrollViewContent}>
      {statesInTamilNadu.map((state, index) => (
        <View key={index} style={styles.weatherReportContainer}>
          <WeatherReport location={state} />
          <View style={styles.spacing} />
        </View>
      ))}
    </ScrollView>
    )
  }


  const styles = StyleSheet.create({
    scrollViewContent: {
      flexGrow: 2,
    },
    weatherReportContainer: {
      marginBottom: 20, 
    },
    spacing: {
      height: 100, 
    },
  })
  
  export default WeatherScreen