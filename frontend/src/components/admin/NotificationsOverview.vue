<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <loader />
    </v-dialog>

    <h2 class="mb-3">Notifications Overview</h2>

    <div v-if="!showLoader">
      <v-card class="pa-5 mb-5">
        <h3>Choose a predefined Notification</h3>
        <p>
          Click on one of the predefined notifications to use it as message
          content.
        </p>

        <v-container class="pt-5 pb-0">
          <v-row class="text-grey d-none d-sm-flex pb-3">
            <v-col cols="2">Title</v-col>
            <v-col cols="10">Message</v-col>
          </v-row>

          <template
            v-for="(notification, index) in initialNotifications"
            :key="index"
          >
            <div>
              <v-hover>
                <template v-slot="{ isHovering, props }">
                  <v-row
                    class="initial-notifications-list-item mb-3"
                    v-bind="props"
                  >
                    <v-col cols="2">{{ notification.title }}</v-col>
                    <v-col cols="10">{{ notification.msg }}</v-col>

                    <div
                      v-show="isHovering"
                      class="list-hover-container align-center justify-center"
                    >
                      <v-btn
                        color="primary"
                        @click="message = notification.msg"
                      >
                        use
                      </v-btn>
                    </div>
                  </v-row>
                </template>
              </v-hover>
            </div>
          </template>
        </v-container>
      </v-card>

      <v-card class="pa-5">
        <h3>Create a new Notification</h3>
        <p>
          Select the user to whom the notification is to be sent. Multiple and
          group selection is possible (duplicate selections will be ignored).
          The position can be used to select the view on which the notification
          is to be displayed.
        </p>

        <div class="mt-5">
          <v-form v-model="form" @submit.prevent="submitHandler">
            <v-container>
              <v-row>
                <v-col cols="8" class="pl-0 pt-0">
                  <v-autocomplete
                    v-model="recipients"
                    :items="resipientsOptions"
                    chips
                    closable-chips
                    label="Recipients"
                    item-title="name"
                    item-value="value"
                    multiple
                    clearable
                    variant="outlined"
                  >
                    <template v-slot:chip="{ props, item }">
                      <v-chip v-bind="props" :text="item.raw.name"></v-chip>
                    </template>

                    <template v-slot:item="{ props, item, index }">
                      <div
                        v-if="props.title.header"
                        class="drop-down-group-title pl-5 pt-5 pb-3 ml-1"
                      >
                        {{ props.title.header }}
                      </div>
                      <div
                        v-else-if="props.title.divider"
                        class="drop-down-divider pt-5 pb-2"
                      >
                        <hr />
                      </div>
                      <v-list-item v-else v-bind="props">
                        <template v-slot:default="{ isActive, toggle }">
                          <v-list-item-action>
                            <v-checkbox
                              :modelValue="isActive"
                              color="primary"
                              @click="toggle"
                            ></v-checkbox>
                          </v-list-item-action>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
                <v-col cols="4" class="pa-0">
                  <v-select
                    label="Position"
                    v-model="positions"
                    :items="positionOptions"
                    multiple
                    clearable
                    closable-chips
                    variant="outlined"
                    chips
                  ></v-select>
                </v-col>
                <v-col cols="12" class="pa-0">
                  <v-textarea
                    label="Message"
                    id="message-textarea"
                    variant="outlined"
                    :model-value="message"
                    @input="message = $event.target.value"
                  >
                    ></v-textarea
                  >
                </v-col>
                <v-col cols="12" class="pa-0 d-flex justify-end">
                  <v-btn
                    :disabled="!form"
                    color="success"
                    size="large"
                    type="submit"
                    variant="elevated"
                  >
                    submit
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </div>
      </v-card>
    </div>
  </div>
</template>

<script lang="ts">
import axios from "axios";

import Loader from "@/components/sub-components/Loader.vue";
import { store } from "@/store";

export default {
  name: "NotificationsOverview",
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
</style>
