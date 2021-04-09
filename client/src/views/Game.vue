<template>
  <div class="game-container">
    <GameIsInvalidModal v-if="gameIsInvalid" />
    <template v-if="!shipsPlaced">
      <ShipPlacement :rows="rows" :cols="cols" />
      <OpponentSelect />
      <button class="button-1" @click="startGame">start game</button>
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
        :ships="ships"
        :board="getBoard(rows, cols, ships)"
        :shots="shots"
        :yours="true"
        :waiting="false"
      />
      <Board
        :rows="rows"
        :cols="cols"
        :ships="opponentShips"
        :board="getBoard(rows, cols, opponentShips)"
        :shots="opponent"
        :yours="false"
        :waiting="!gameStarted && shipsPlaced"
      />
      <div>
        <button class="button-1 leave-button" @click="leaveGame">
          leave game
        </button>
      </div>
    </template>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { zeros, getBoard } from "../helpers";
import ShipPlacement from "@/components/ShipPlacement.vue";
import OpponentSelect from "@/components/OpponentSelect.vue";
import Status from "@/components/Status.vue";
import Board from "@/components/Board.vue";
import GameIsInvalidModal from "@/components/GameIsInvalidModal.vue";
export default {
  components: {
    ShipPlacement,
    Status,
    Board,
    OpponentSelect,
    GameIsInvalidModal
  },
  data() {
    return {
      dummyBoard: [],
      showModal: false
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
      "opponentShips",
      "yourTurn",
      "opponentLeft",

      "shipsPlaced",
      "gameStarted",
      "gameId",
      "gameIsInvalid"
      // "link",
    ]),
    link() {
      return document.URL + "join" + this.gameId;
    }
  },
  created() {
    this.dummyBoard = zeros(this.rows, this.cols, 0);
    this.$store.dispatch("initSocket", {
      handler: this.onGameUpdate
    });
    window.addEventListener("beforeunload", this.beforeWindowUnload);
  },

  methods: {
    getBoard,
    ...mapActions([
      "onSocketMessage",
      "updateGame",
      "startGame",
      "leaveGame",
      "resetGame"
    ]),
    beforeWindowUnload(event) {
      if (this.gameStarted && !this.opponentLeft) {
        event.preventDefault();
        event.returnValue = "";
        return null;
      }
    },
    onGameUpdate(event) {
      let data = JSON.parse(event.data);
      this.onSocketMessage(data);
    },
    copyLink() {
      this.$clipboard(this.link);
      alert("Link was copied!");
    }
  }
};
</script>
