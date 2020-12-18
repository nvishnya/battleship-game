<template>
  <div class="game">
    <template v-if="!shipsPlaced">
      <ShipPlacement :rows="rows" :cols="cols" />
      <div class="opponent-select">
        opponent:
        <button
          :class="{ selected: friendAsOpponent == false }"
          class="op-btn"
          @click="createGameWithRandomOpponent"
        >
          random</button
        >/
        <button
          :class="{ selected: friendAsOpponent == true }"
          class="op-btn"
          @click="createGameWithFriendOpponent"
        >
          friend
        </button>
      </div>
      <div>
        <button class="btn" @click="startGame">start</button>
      </div>
    </template>

    <div
      v-if="friendAsOpponent && shipsPlaced && !gameStarted"
      :style="{ marginTop: '25px' }"
    >
      <div>send this link to your frined:</div>
      <div @click="copyLink" :style="{ color: 'blue', marginTop: '10px' }">
        [{{ link }}]
      </div>
    </div>

    <template v-if="shipsPlaced">
      <Status :waiting="!gameStarted && shipsPlaced" />
      <Board
        :rows="rows"
        :cols="cols"
        :board="board"
        :shots="shots"
        :yours="true"
        :waiting="false"
      />
      <Board
        :rows="rows"
        :cols="cols"
        :board="dummyBoard"
        :shots="opponent"
        :yours="false"
        :waiting="!gameStarted && shipsPlaced"
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
      "link",
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
    copyLink() {
      this.$clipboard(this.link);
      alert("Link was copied!");
    },
  },
};
</script>
