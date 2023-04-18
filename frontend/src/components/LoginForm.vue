<template>
  <div>
    <error v-if="error_msg" :msg="error_msg" />
    <v-row class="align-center justify-center" style="height: 100vh">
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
  </div>
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";
import axios from "axios";
import Error from "@/components/sub-components/Error.vue";
import { setStyles } from "@/helpers";

export default {
  name: "LoginForm",
  components: {
    SvgIcon,
    Error,
  },
  data() {
    return {
      headline: "",
      headlineHighlight: "",
      welcomeText: "",
      showPassword: false,
      form: false,
      username: null,
      password: null,
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
        // store.dispatch("getTabsFromServer");
        this.$router.push("/");
      } else {
        store.dispatch("unsetJwt");
        axios.defaults.headers.common["Authorization"] = "";
        store.dispatch("setError", "Invalid username or password.");
      }
    },
  },
  async beforeMount() {
    setStyles(this);

    const response = await axios.get("setup/login");
    console.log(response);
    this.headline = response?.data.headline || "Welcome to";
    this.headlineHighlight = response?.data.headlineHighlight || "Learners";
    this.welcomeText = response?.data.welcomeText || "";
    store.dispatch("resetTabs");

    // const styleResponse = await axios.get("setup/styles");
    // console.log(this.$vuetify.theme.themes.light);
    // for (const key in styleResponse?.data.theme) {
    //   this.$vuetify.theme.themes.light.colors[key] =
    //     styleResponse?.data.theme[key];
    // }
    // store.dispatch("setLogo", styleResponse?.data.logo);
    // store.dispatch("setCurrentView", response?.data.landingpage);
  },
};
</script>
