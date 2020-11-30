<template>
  <div class="game">
    <!-- GAME NOT STARTED YET -->
    <template v-if="!shipsPlaced">
      <ShipPlacement :rows="rows" :cols="cols" />
      <div class="opponent-select">
        opponent:
        <span>friend</span>/random
      </div>
      <div>
        <button class="btn" @click="startGame">start</button>
      </div>
    </template>

    <div v-if="friendAsOpponent && shipsPlaced && !gameStarted">
      send this link to your frined:
    </div>

    <template v-if="gameStarted">
      <Status :yourTurn="yourTurn" />
      <!-- YOU -->
      <Board
        :rows="rows"
        :cols="cols"
        :board="board"
        :shots="shots"
        :yours="true"
      />
      <Board
        :rows="rows"
        :cols="cols"
        :board="dummyBoard"
        :shots="opponent"
        :yours="false"
      />
    </template>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { zeros } from "../helpers";
import ShipPlacement from "@/components/ShipPlacement.vue";
import Status from "@/components/Status.vue";
import Board from "@/components/Board.vue";

export default {
  components: {
    ShipPlacement,
    Status,
    Board,
  },
  data() {
    return {
      dummyBoard: [],
    };
  },
  computed: {
    ...mapState([
      "socket",
      "savedGameId",
      "friendAsOpponent",
      "rows",
      "cols",
      "ships",

      "board",
      "shots",
      "opponent",
      "yourTurn",

      "shipsPlaced",
      "gameStarted",
    ]),
  },
  created() {
    this.dummyBoard = zeros(this.rows, this.cols, 0);
    this.$store.dispatch("initSocket", {
      handler: this.onGameUpdate,
      reloadShips: true,
    });
  },
  methods: {
    ...mapActions([
      "createGameWithFriendOpponent",
      "createGameWithRandomOpponent",
      "onSocketMessage",
      "updateGame",
      "startGame",
    ]),
    onGameUpdate(event) {
      let data = JSON.parse(event.data);
      this.onSocketMessage(data);
    },
  },
};
</script>
