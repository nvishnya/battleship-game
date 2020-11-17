<template>
  <div>
    <ShipPlacement :rows="size.rows" :cols="size.cols" />
    <!-- <button @click="createGameWithFriendOpponent(size)">
      Game With Friend
    </button>
    <button @click="createGameWithRandomOpponent">
      Game With Random
    </button>
    <button @click="startGame">
      Start Game
    </button> -->
    <!-- <button @click="getRandomlyPositionedShips">Randomize</button> -->
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import ShipPlacement from "@/components/ShipPlacement.vue";

export default {
  components: {
    ShipPlacement,
  },
  data() {
    return {
      // custom size for a game with a friend only!
      loading: false,

      size: { rows: 10, cols: 10 },
      ships: [],

      field: null,
      shots: null,
    };
  },
  computed: {
    ...mapState(["socket"]),
  },
  created() {
    this.$store.dispatch("initSocket", { handler: this.onGameUpdate });
  },
  methods: {
    ...mapActions([
      "createGameWithFriendOpponent",
      "createGameWithRandomOpponent",
      "sendSocketMessage",
    ]),
    onGameUpdate(event) {
      console.log("it works!: ", event);
    },
    async getRandomlyPositionedShips() {
      const response = await this.axios.get(
        `random-board/?rows=${this.size.rows}&cols=${this.size.cols}`
      );
      this.ships = response.data;
    },

    startGame() {
      let payload = {
        command: "start",
        ships: this.ships,
        ...this.size,
      };
      this.sendSocketMessage(payload);
    },

    makeMove(x, y) {
      let payload = {
        command: "move",
        x: x,
        y: y,
      };
      this.sendSocketMessage(payload);
    },
  },
};
</script>
