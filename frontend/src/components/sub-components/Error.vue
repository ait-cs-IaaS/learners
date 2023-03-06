<template>
  <v-snackbar
    :model-value="msg?.length > 0"
    multi-line
    timeout="100000"
    absolute
    appear
    class="error-container"
    variant="flat"
    rounded="4"
  >
    {{ msg }}
  </v-snackbar>

  <!-- <Transition :duration="5500" appear>
    <div v-if="msg?.length > 0" style="background: green">
      {{ msg }}
    </div>
  </Transition> -->
</template>

<script lang="ts">
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";

export default {
  name: "Error",
  components: {
    SvgIcon,
  },
  props: {
    msg: { type: String, require: true, default: "" },
  },
};
</script>

<style lang="scss">
.error-container {
  .v-snackbar__wrapper {
    background-color: #d49595;
  }
}
</style>
