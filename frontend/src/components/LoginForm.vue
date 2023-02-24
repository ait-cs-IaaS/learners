<template>
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
              :rules="[rules.required]"
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
              :rules="[rules.required]"
              :type="showPassword ? 'text' : 'password'"
              name="input-10-1"
              label="Password"
              hint="Enter provided password"
              variant="outlined"
              counter
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
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";
import axios from "axios";

export default {
  name: "LoginForm",
  components: {
    SvgIcon,
  },
  data() {
    return {
      headline: "Welcome to",
      headlineHighlight: "Leaners",
      welcomeText: "",
      showPassword: false,
      form: false,
      username: null,
      password: null,

      rules: {
        required: (value) => !!value || "Required.",
      },
    };
  },
  created() {
    (async () => {
      const response = await axios.get("setup/login");
      this.headline = response.data.headline || "Welcome to";
      this.headlineHighlight = response.data.headlineHighlight || "Learners";
      this.welcomeText = response.data.welcomeText || "";
      await store.dispatch("setCurrentView", response.data.landingpage);
      await store.dispatch("setLogo", response.data.logo);
    })();
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
        store.dispatch("getTabsFromServer");
      }
    },
  },
};
</script>
