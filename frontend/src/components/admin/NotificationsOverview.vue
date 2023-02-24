<template>
  <div>
    <v-dialog v-model="showLoader" :scrim="false" persistent width="auto">
      <loader />
    </v-dialog>

    <h2 class="mb-3">Notifications Overview</h2>

    <div v-if="!showLoader">
      <h3>Choose a predefined Notification</h3>
      <p>
        Click on one of the predefined notifications to use it as message
        content.
      </p>

      <v-card variant="flat" class="pa-0 mt-2 mb-5">
        <v-container class="pa-5">
          <v-row class="text-grey d-none d-sm-flex">
            <v-col cols="2">Title</v-col>
            <v-col cols="10">Message</v-col>
          </v-row>
          <v-row v-for="notification in initialNotifications">
            <v-col cols="2">{{ notification.title }}</v-col>
            <v-col cols="10">{{ notification.msg }}</v-col>
          </v-row>
        </v-container>
      </v-card>

      <h3>Create a new Notification</h3>
      <p>
        Select the user to whom the notification is to be sent. Multiple and
        group selection is possible (duplicate selections will be ignored). The
        position can be used to select the view on which the notification is to
        be displayed.
      </p>

      <div class="mt-5">
        <v-form>
          <v-container>
            <v-autocomplete
              v-model="selectedRecipients"
              :items="users"
              chips
              closable-chips
              label="Recipients"
              item-title="name"
              item-value="value"
              multiple
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
                <v-list-item v-else v-bind="props" @click="debuglog">
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
          </v-container>
        </v-form>
      </div>
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
      notificationLoading: false,
      usersLoading: false,
      groupsLoading: false,
      autoUpdate: true,
      selectedRecipients: [],
      users: <any>[],
      people: [
        { header: "Group 1" },
        { name: "Sandra Adams" },
        { name: "Ali Connors" },
        { name: "Trevor Hansen" },
        { name: "Tucker Smith" },
        { divider: true },
        { header: "Group 2" },
        { name: "Britta Holt" },
        { name: "Jane Smith " },
        { name: "John Smith" },
        { name: "Sandra Williams" },
      ],
    };
  },
  props: {
    currentTab: { type: String, require: false },
  },
  computed: {
    showLoader() {
      const viewCondition = store.getters.getCurrentView === "admin";
      const tabCondition = this.currentTab === "Notifications";
      const eventCondition = this.loading;
      return viewCondition && tabCondition && eventCondition;
    },
    loading() {
      return this.usersLoading || this.notificationLoading;
    },
  },
  methods: {
    debuglog() {
      console.log(this.selectedRecipients);
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
        this.users.push({
          header: "Users",
        });
        users.forEach((user) => {
          this.users.push({
            name: user.name,
            value: user.id,
          });
        });
        this.users.push({
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
        this.users.push({
          header: "Groups",
        });
        groups.forEach((group) => {
          this.users.push({
            name: group.name,
            value: group.ids,
          });
        });
        this.users.push({
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
</style>
