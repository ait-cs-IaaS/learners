<template>
  <div :style="style" class="align-self-center">
    <h5 class="text-center">{{ text }}</h5>
    <v-progress-linear
      class="mt-3 mb-3"
      color="primary"
      indeterminate
      rounded
      height="6"
    ></v-progress-linear>
  </div>
</template>

<script lang="ts">
export default {
  name: "Loader",
  props: {
    text: {
      type: String,
      require: false,
      default: "Requesting data ...",
    },
    width: {
      type: String,
      require: false,
      default: "100%",
    },
  },
  computed: {
    style() {
      return "width: " + this.width;
    },
  },
};
</script>
