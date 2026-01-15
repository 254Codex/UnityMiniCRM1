import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'navyTheme',
    themes: {
      navyTheme: {
        dark: false,
        colors: {
          primary: '#001f3f',      // Navy Blue
          secondary: '#0074D9',     // Lighter Blue
          accent: '#39CCCC',        // Teal
          error: '#FF4136',
          warning: '#FF851B',
          info: '#0074D9',
          success: '#2ECC40',
          background: '#f5f7fa',
        },
      },
    },
  },
})
