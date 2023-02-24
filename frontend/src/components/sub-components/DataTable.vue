<template>
  <EasyDataTable :headers="headers" :items="items">
    <template #loading>
      <loader />
    </template>

    <template
      v-for="header in headers"
      v-slot:[getSlotName(header.value)]="data"
    >
      <div :key="header.value" :data="data">
        <success-icon
          class="clickable"
          v-if="data[header.value].completed === 1"
          @click="
            $emit('showDetails', {
              userId: data['user_id'],
              exerciseId: header.value,
            })
          "
        />

        <fail-icon
          class="clickable"
          v-else-if="
            data[header.value].completed === -1 &&
            data[header.value].executions.len > 0
          "
        />
        <span v-else-if="header.value === 'username'">{{
          data[header.value]
        }}</span>

        <span v-else> - </span>
      </div>
    </template>
  </EasyDataTable>
</template>

<script lang="ts">
import type { Header, Item } from "vue3-easy-data-table";
import SuccessIcon from "@/components/sub-components/SuccessIcon.vue";
import FailIcon from "@/components/sub-components/FailIcon.vue";
import Loader from "@/components/sub-components/Loader.vue";

export default {
  name: "DataTable",
  components: {
    SuccessIcon,
    FailIcon,
    Loader,
  },
  props: {
    headers: {
      type: Array<Header>,
      require: true,
    },
    items: {
      type: Array<Item>,
      require: true,
    },
  },

  methods: {
    getSlotName(value) {
      return `item-${value}`;
    },
  },
};
</script>
