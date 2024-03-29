// Styles

import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";

// Composables
import { createVuetify } from "vuetify";

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#f6f6f6",
          secondary: "#666666",
          success: "#70ae70",
          warning: "#c12f2f",
          info: "#dbb469",
        },
      },
    },
  },
});
