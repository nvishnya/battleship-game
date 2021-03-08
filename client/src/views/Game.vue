<template>
  <div>
    <Modal v-if="gameIsInvalid">
      <div>Sorry, this game is unavailable.</div>
      <button @click="resetGame" class="blue-button modal-button">OK</button>
    </Modal>
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
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { zeros } from "../helpers";
import ShipPlacement from "@/components/ShipPlacement.vue";
import Status from "@/components/Status.vue";
import Board from "@/components/Board.vue";
import Modal from "@/components/Modal.vue";
export default {
  components: {
    ShipPlacement,
    Status,
    Board,
    Modal,
  },
  data() {
    return {
      dummyBoard: [],
      showModal: false,
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
      "opponentLeft",

      "shipsPlaced",
      "gameStarted",
      "gameId",
      "gameIsInvalid",
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
    });
    window.addEventListener("beforeunload", this.beforeWindowUnload);
  },

  methods: {
    ...mapActions([
      "createGameWithFriendOpponent",
      "createGameWithRandomOpponent",
      "onSocketMessage",
      "updateGame",
      "startGame",
      "leaveGame",
      "resetGame",
    ]),
    beforeWindowUnload(event) {
      if (this.gameStarted && !this.opponentLeft) {
        event.preventDefault();
        event.returnValue = "";
        console.log(event);
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
    },
  },
};
</script>
