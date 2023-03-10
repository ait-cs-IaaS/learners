<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <loader />
    </v-dialog>

    <h2 class="mb-3">Feedback Overview</h2>

    <div v-if="!showLoader">bla</div>
  </div>
</template>

<script lang="ts">
import axios from "axios";

import Loader from "@/components/sub-components/Loader.vue";
import { store } from "@/store";

export default {
  name: "FeedbackOverview",
  components: {
    Loader,
  },
  data() {
    return {
      initialNotifications: <any>[],
      // Loader conditions
      notificationLoading: false,
      usersLoading: false,
      groupsLoading: false,
      // Form
      form: false,
      // Recipients
      recipients: [],
      resipientsOptions: <any>[],
      // Positions
      positions: ["all"],
      positionOptions: ["documentation", "exercises", "clients", "all"],
      // Message
      message: "",
    };
  },
  props: {
    currentTab: { type: String, require: false },
  },
  computed: {
    showLoader() {
      const viewCondition = store.getters.getCurrentView === "admin";
      const tabCondition = this.currentTab === "Notifications";
      const eventCondition = this.usersLoading || this.notificationLoading;
      return viewCondition && tabCondition && eventCondition;
    },
  },
  methods: {
    async submitHandler() {
      if (!this.form) return;

      const recipients = this.recipients.flatMap((num) => num);
      const dedubRecipients = [...new Set(recipients)];

      const response = await axios.post("notifications", {
        recipients: dedubRecipients,
        message: this.message,
        positions: this.positions,
      });

      console.log(response);
    },
  },
  async beforeMount() {
    this.notificationLoading = true;
    axios
      .get("setup/notifications")
      .then((res) => {
        this.initialNotifications = res.data.initialNotifications;
      })
      .finally(() => {
        this.notificationLoading = false;
      });

    this.usersLoading = true;
    axios
      .get("users")
      .then((res) => {
        const users = res.data.users;
        this.resipientsOptions.push({
          header: "Users",
        });
        users.forEach((user) => {
          this.resipientsOptions.push({
            name: user.name,
            value: user.id,
          });
        });
        this.resipientsOptions.push({
          divider: true,
        });
      })
      .finally(() => {
        this.usersLoading = false;
      });

    this.groupsLoading = true;
    axios
      .get("usergroups")
      .then((res) => {
        const groups = res.data.groups;
        this.resipientsOptions.push({
          header: "Groups",
        });
        groups.forEach((group) => {
          this.resipientsOptions.push({
            name: group.name,
            value: group.ids,
          });
        });
        this.resipientsOptions.push({
          divider: true,
        });
      })
      .finally(() => {
        this.groupsLoading = false;
      });
  },
};
</script>

<style lang="scss">
.drop-down-group-title {
  font-weight: bold;
}

.v-list-item {
  padding-top: 0px !important;
  padding-bottom: 0px !important;
}
.v-list-item__content {
  display: flex;
  flex-direction: row-reverse;
  justify-content: start;
  align-content: center;
}

.v-list-item-title {
  flex: 1;
  align-self: center;
  height: 100%;
  width: 100%;
}
.v-list-item-subtitle {
  flex: 1;
  align-self: center;
}

.v-list-item-action {
  align-content: center;
  justify-content: center;
  display: flex;
  height: 45px;
  max-width: 20%;
}

.v-input.v-checkbox {
  display: flex;
}

.initial-notifications-list-item {
  position: relative;
  background-color: #f6f6f6;
  margin-top: 0px;
  border-radius: 4px;
}

.list-hover-container {
  display: flex;
  position: absolute;
  background-color: rgba(var(--v-theme-primary), 0);
  width: 100%;
  height: 100%;
  transition: all 150ms ease;
  border-radius: 4px;

  &:hover {
    background-color: rgba(var(--v-theme-primary), 0.1);
  }

  button.v-btn {
    background-color: white;
    border: solid 1px #555;
  }
}

.autocomplete-inputs .v-input__control {
  min-height: 60px;
}
</style>
