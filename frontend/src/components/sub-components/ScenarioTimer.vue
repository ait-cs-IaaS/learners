<template>
  <div class="time-container">
    <span class="time">{{ time }}</span>

    <div class="btn-container">
      <SvgIcon
        name="chevron-double-left"
        inline
        clickable
        @click="changeOffset(-60)"
      />

      <SvgIcon v-if="!running" name="play" inline clickable @click="start()" />

      <SvgIcon v-else name="pause" inline clickable @click="pause()" />

      <SvgIcon name="x-mark" inline clickable @click="reset()" />

      <SvgIcon
        name="chevron-double-right"
        inline
        clickable
        @click="changeOffset(60)"
        class="mr-0"
      />
    </div>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import SvgIcon from "@/components/dynamic-components/SvgIcon.vue";
import { store } from "@/store";

export default {
  name: "ScenarioTimer",
  components: {
    SvgIcon,
  },
  data() {
    return {
      time: "00:00:00",
      timeBegan: null as any | null,
      timeStopped: null as any | null,
      stoppedDuration: 0,
      started: null as any | null,
      running: false,
      offset: 0,
    };
  },
  computed: {
    store_timer() {
      return store.getters.getTimer;
    },
  },
  methods: {
    utcNow() {
      return new Date(new Date().toUTCString().split("GMT")[0]);
    },
    async start() {
      if (!this.timeBegan) {
        await axios.post(`/time/start`);
      } else {
        await axios.post(`/time/continue`);
      }
    },

    pause() {
      axios.post(`/time/pause`);
    },

    reset() {
      axios.post(`/time/reset`);
    },

    changeOffset(_delta) {
      this.offset += _delta * 1000;
      axios.post(`/time/offset`, { offset: this.offset });
    },

    handleStart() {
      this.started = setInterval(this.displayTime, 1000);
    },

    displayTime(currentTime) {
      if (!currentTime) {
        currentTime = this.utcNow();
      }
      let timeElapsed = new Date(
        currentTime.getTime() - this.timeBegan + this.offset
      );

      const zeroPad = (num) => String(num).padStart(2, "0");
      let hour = zeroPad(timeElapsed.getUTCHours());
      let min = zeroPad(timeElapsed.getUTCMinutes());
      let sec = zeroPad(timeElapsed.getUTCSeconds());
      this.time = `${hour}:${min}:${sec}`;
    },

    newStateHandle() {
      if (this.timeBegan) {
        if (this.running) {
          this.handleStart();
        } else {
          this.displayTime(this.timeStopped);
          clearInterval(this.started);
        }
      } else {
        this.time = "00:00:00";
      }
    },
  },
  mounted() {
    axios.get(`/time`);
  },
  watch: {
    store_timer: {
      handler(new_state, old_state) {
        if (new_state) {
          if (new_state.start_time) {
            this.timeBegan = new Date(
              new Date(new_state.start_time).toUTCString().split("GMT")[0]
            );
          } else {
            this.timeBegan = null;
          }

          if (new_state.pause_time) {
            this.timeStopped = new Date(
              new Date(new_state.pause_time).toUTCString().split("GMT")[0]
            );
          } else {
            this.timeStopped = null;
          }

          this.offset = new_state?.offset;

          this.running = Boolean(new_state.running);
        }

        clearInterval(this.started);

        this.newStateHandle();
      },
      immediate: true,
    },
  },
};
</script>

<style lang="scss">
.time-container {
  display: flex;
  padding-top: 5px;
  text-align: center;

  & svg {
    opacity: 0.6;
    transition: opacity 0.1s ease-out;
    &:hover {
      opacity: 1;
    }
  }
}

.time {
  font-family: "Roboto Mono", monospace;
  font-weight: 400;
  font-size: 2em;
}

.btn-container {
  width: fit-content;
  margin: auto;
  margin-left: 16px;
}
</style>
