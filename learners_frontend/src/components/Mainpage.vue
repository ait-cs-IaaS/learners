<template>
  <div class="fill-height d-flex">
    <Transition name="fade" mode="in-out">
      <iframe
        v-show="currentView === 'documentation'"
        src="http://localhost:5000/login"
        frameborder="0"
        class="content-container pager exercises"
        noresize="noresize"
      ></iframe>
    </Transition>

    <Transition name="fade">
      <iframe
        v-show="currentView === 'client'"
        src="https://novnc.demo.cyberrange.rocks/?auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NDQ3NTk5NywianRpIjoiN2Q1ODQxNDktNzVjZi00OGNhLWE1YjktZDUwYThmMDY4OGJjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRvc2l2YXhfY3NpcnQyIiwibmJmIjoxNjc0NDc1OTk3LCJjc3JmIjoiNGNjZjQ0MzQtYjMyMy00MGNhLTkxZDUtZTgwYTEwYTlkYTlhIiwiZXhwIjoxNjc0NTE5MTk3LCJ0YXJnZXQiOiJkb3NpdmF4X2NzaXJ0X2NsaWVudF8yIiwidXNlcm5hbWUiOiJjc2lydDIiLCJwYXNzd29yZCI6Im1vemFydC5yb2NrcyJ9.PbqYyiD4LmujeeKzyn6YS7CVVUBBW8jg4t85Li7NJj4"
        frameborder="0"
        class="content-container pager exercises"
        noresize="noresize"
      ></iframe>
    </Transition>
  </div>
</template>

<script lang="ts">
// import axios from "axios";

export default {
  name: "Mainpage",
  computed: {
    currentView() {
      return this.$store.state.currentView;
    },
  },
  async created() {
    // const response = await axios.get("/access");
    // console.log(response);
  },
};
</script>
