<template>
  <div class="game">
    <template v-if="!shipsPlaced">
      <ShipPlacement :rows="rows" :cols="cols" />
      <div class="opponent-select">
        opponent:
        <template v-if="gameId == null">
          <button
            :class="{ 'selected-opponent': friendAsOpponent == false }"
            class="link-button"
            @click="createGameWithRandomOpponent"
          >
            random</button
          >/
        </template>
        <button
          :class="{ 'selected-opponent': friendAsOpponent == true }"
          class="link-button"
          @click="createGameWithFriendOpponent"
        >
          friend
        </button>
      </div>
      <div>
        <button class="orange-button" @click="startGame">start</button>
      </div>
    </template>

    <div v-if="friendAsOpponent && shipsPlaced && !gameStarted">
      <div class="link-for-a-friend">
        send this link to your frined:
        <span @click="copyLink" class="link-itself">{{ link }}</span>
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
      <div>
        <button class="red-button" @click="leaveGame">leave game</button>
      </div>
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
      "gameId",
      // "link",
    ]),
    link() {
      return document.URL + "join" + this.gameId;
    },
  },
  created() {
    this.dummyBoard = zeros(this.rows, this.cols, 0);
    this.$store.dispatch("initSocket", {
      handler: this.onGameUpdate,
      // reloadShips: true,
    });
  },
  methods: {
    ...mapActions([
      "createGameWithFriendOpponent",
      "createGameWithRandomOpponent",
      "onSocketMessage",
      "updateGame",
      "startGame",
      "leaveGame",
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
