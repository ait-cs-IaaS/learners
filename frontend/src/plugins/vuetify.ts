// Styles

import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";

// Composables
import { createVuetify } from "vuetify";

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    themes: {
      light: {
        colors: {
          primary: "#0072bc",
          secondary: "#5CBBF6",
          success: "#70ae70",
          warning: "#c12f2f",
        },
      },
    },
  },
});
