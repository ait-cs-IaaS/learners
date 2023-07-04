<template>
  <div>
    <div v-if="loaded">
      <v-row class="align-center justify-center" style="height: 100vh">
        <v-col>
          <v-row>
            <v-col offset="1">
              <h1 class="main-title">
                {{ headline }}
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
                  class="mb-2"
                  variant="outlined"
                  clearable
                  label="Username"
                >
                  <template v-slot:prepend-inner>
                    <SvgIcon name="user" />
                  </template>
                </v-text-field>

                <v-text-field
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  label="Password"
                  variant="outlined"
                >
                  <template v-slot:prepend-inner>
                    <SvgIcon name="key" />
                  </template>
                  <template v-slot:append-inner>
                    <div @click="showPassword = !showPassword">
                      <SvgIcon v-if="showPassword" name="eye" clickable />
                      <SvgIcon v-else name="eye-slash" clickable />
                    </div>
                  </template>
                </v-text-field>

                <v-btn
                  :disabled="!form"
                  color="success"
                  size="large"
                  type="submit"
                  variant="elevated"
                >
                  <SvgIcon name="arrow-left-on-rectangle" inline /> sign in
                </v-btn>
              </v-form>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>

    <transition v-if="!loaded || error">
      <div class="fullscreen-center" style="z-index: 9999">
        <loader
          width="20%"
          class="mx-auto"
          :loadingTxt="loadingText"
          :errorTxt="errorText"
          :timeout="5"
        />
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";
import axios from "axios";
import { setStyles } from "@/helpers";
import Loader from "@/components/sub-components/Loader.vue";

export default {
  name: "LoginForm",
  components: {
    SvgIcon,
    Loader,
  },
  data() {
    return {
      headline: "",
      welcomeText: "",
      showPassword: false,
      form: false,
      username: null,
      password: null,
      loaded: false,
      error: false,
      loadingText: "Connecting to server ...",
      errorText: "",
    };
  },
  computed: {
    error_msg: () => store.getters.getError,
  },
  methods: {
    async submitHandler() {
      if (!this.form) return;
      const response = await axios.post("login", {
        username: this.username,
        password: this.password,
      });

      const jwt = response.data.jwt;
      if (jwt) {
        store.dispatch("setJwt", jwt);
        axios.defaults.headers.common["Authorization"] = "Bearer " + jwt;
        this.$router.push("/");
      } else {
        store.dispatch("unsetJwt");
        axios.defaults.headers.common["Authorization"] = "";
        store.dispatch("setError", "Invalid username or password.");
      }
    },
  },
  async beforeMount() {
    this.headline = "Login";
    this.welcomeText = "";

    store.dispatch("resetTabs");

    const connectToServer = (ctx) => {
      let attemptCount = 1;

      const makeConnection = (context) => {
        axios
          .get("setup/login")
          .then((response) => {
            setStyles(context);
            context.headline = response?.data.headline || "Welcome to Learners";
            context.welcomeText = response?.data.welcomeText || "";
            context.loaded = true;
            context.error = false;
          })
          .catch((error) => {
            console.log(context);
            context.error = true;
            if (error.response) {
              context.errorText = `Encounted error on server: <br> <strong>${error.response.status}</strong> <br> ${error.response.data} <br><br> Retrying in 5 seconds ... (${attemptCount})`;
            } else if (error.request) {
              context.errorText = `Unable to connect to the server. <br> Make sure the server can be reached and the certificate (if self-signed) is accepted. In order verify this, go to <a href="${
                import.meta.env.VITE_BACKEND
              }">${
                import.meta.env.VITE_BACKEND
              }</a> and accept the certificate if prompted. <br><br> Retrying in 5 seconds ... (${attemptCount})`;
            } else {
              context.errorText = `Error in setting up the request to the server: <br> ${error.message} <br><br> Retrying in 5 seconds ... (${attemptCount})`;
            }
            setTimeout(() => {
              attemptCount++;
              console.log(attemptCount);
              makeConnection(context);
            }, 5000);
          });
      };

      makeConnection(ctx);
    };

    connectToServer(this);

    setStyles(this);

    // const response = await axios.get("setup/login");
    // if (response) {
    //   this.headline = response?.data.headline || "Welcome to Learners";
    //   this.welcomeText = response?.data.welcomeText || "";
    //   store.dispatch("resetTabs");
    // } else {
    //   this.headline = "Welcome to Learners";
    //   this.welcomeText = "bla";
    //   store.dispatch("resetTabs");
    // }
  },
};
</script>
