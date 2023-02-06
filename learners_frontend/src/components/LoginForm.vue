<template>
  <v-row class="fill-height align-center justify-center">
    <v-col>
      <v-row>
        <v-col offset="1">
          <h1 class="main-title">
            {{ headline }}
            <span>{{ headlineHighlight }}</span>
          </h1>
        </v-col>
      </v-row>

      <v-row>
        <v-col offset="1">
          <!-- eslint-disable vue/no-v-html -->
          <div v-html="welcomeText" />
          <!--eslint-enable-->
        </v-col>
      </v-row>

      <v-row class="align-start justify-start">
        <v-col offset="1" xl="3" lg="4" md="6" cols="10">
          <v-form v-model="form" @submit.prevent="submitHandler">
            <v-text-field
              v-model="username"
              :rules="[rules.required]"
              prepend-inner-icon="mdi-account-outline"
              class="mb-2"
              variant="outlined"
              clearable
              label="Username"
            />

            <v-text-field
              v-model="password"
              :append-inner-icon="
                showPassword ? 'mdi-eye-outline' : 'mdi-eye-off-outline'
              "
              :rules="[rules.required]"
              :type="showPassword ? 'text' : 'password'"
              prepend-inner-icon="mdi-lock-outline"
              name="input-10-1"
              label="Password"
              hint="Enter provided password"
              variant="outlined"
              counter
              @click:append="showPassword = !showPassword"
            />

            <v-btn
              :disabled="!form"
              block
              color="success"
              size="large"
              type="submit"
              variant="elevated"
            >
              Sign In
            </v-btn>
          </v-form>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import axios from "axios";
import ymlconfig from "../../../frontend_config.yml";

export default {
  name: "LoginForm",
  data() {
    return {
      headline: ymlconfig.headline || "Welcome to",
      headlineHighlight: ymlconfig.headlineHighlight || "Leaners",
      welcomeText: ymlconfig.welcomeText || "",
      showPassword: false,
      form: false,
      username: null,
      password: null,

      rules: {
        required: (value) => !!value || "Required.",
      },
    };
  },
  methods: {
    async submitHandler() {
      if (!this.form) return;

      // const data = {
      //   username: this.username || "",
      //   password: this.password || "",
      // };

      const response = await axios.post("login", {
        username: this.username || "",
        password: this.password || "",
      });

      console.log(response);
      //     .then((res) => {
      //       console.log(res.data);
      //     })
      //     .catch((err) => {
      //       console.log(err);
      //     });

      localStorage.setItem("token", response.data.token);

      if (response.data.authenticated) {
        this.$router.push("/");
      }
    },
  },
};
</script>
