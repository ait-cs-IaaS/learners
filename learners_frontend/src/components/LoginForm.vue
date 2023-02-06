<template>
  <v-container class="fill-height">
    <v-responsive class="d-flex align-center text-center fill-height">
      <h1>
        {{ headline }}
        <span>{{ headlineHighlight }}</span>
      </h1>

      <!-- eslint-disable vue/no-v-html -->
      <div v-html="welcomeText" />
      <!--eslint-enable-->

      <div class="py-14" />

      <v-row class="d-flex align-center justify-center">
        <v-col cols="2">
          <v-form v-model="form" @submit.prevent="onSubmit">
            <v-text-field
              v-model="username"
              :readonly="loading"
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
              :loading="loading"
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
    </v-responsive>
  </v-container>
</template>

<script lang="ts">
import axios from "axios";
import DOMPurify from "dompurify";
import { marked } from "marked";

export default {
  name: "LoginForm",
  data: () => ({
    headline: "",
    headlineHighlight: "",
    welcomeText: "",
    showPassword: false,
    form: false,
    username: null,
    password: null,
    loading: false,

    rules: {
      required: (value) => !!value || "Required.",
    },
  }),
  created() {
    this.getResponse();
  },
  methods: {
    onSubmit() {
      if (!this.form) return;

      this.loading = true;

      const formData = new FormData();
      formData.append("username", this.username || "");
      formData.append("password", this.password || "");

      const path = "http://localhost:5000/login";
      console.log(formData);
      axios
        .post(path, formData)
        .then((res) => {
          console.log(res.data);
        })
        .catch((err) => {
          console.log(err);
        });

      setTimeout(() => (this.loading = false), 2000);
    },
    transformAndClearBody(body) {
      const htmlBody = marked.parse(body);
      const sanitizedBody = DOMPurify.sanitize(htmlBody);
      return sanitizedBody;
    },
    getResponse() {
      const path = "http://localhost:5000";
      axios
        .get(path)
        .then((res) => {
          console.log(res.data);
          this.headline = res.data.headline;
          this.headlineHighlight = res.data.headlineHighlight;
          this.welcomeText = this.transformAndClearBody(res.data.welcomeText);
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
};
</script>
