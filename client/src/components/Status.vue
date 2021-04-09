<template>
  <div class="game-status">
    <p
      v-if="!waiting && !isOver && !opponentLeft"
      :class="[
        !waiting && yourTurn ? 'status-your-turn' : 'status-opponents-turn ',
      ]"
    >
      It's {{ yourTurn ? "YOUR" : "OPPONENT'S" }} turn.
    </p>
    <p v-if="waiting" class="status-waiting">Waiting for an opponent.</p>
    <p v-if="isOver" :class="youWon ? 'status-you-won' : 'status-you-lost'">
      Game over. You {{ youWon ? "won!" : "lost!" }}
    </p>
    <p v-if="opponentLeft && !isOver" class="status-opponent-left">
      Opponent has left the game.
    </p>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  props: {
    waiting: Boolean,
  },
  computed: {
    ...mapState([
      "shipsPlaced",
      "gameStarted",
      "yourTurn",
      "isOver",
      "youWon",
      "opponentLeft",
    ]),
  },
};
</script>
