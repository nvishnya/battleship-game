<template>
  <div class="">
    <p v-if="!waiting && !isOver && !opponentLeft" class="waiting-for-opponent">
      It's {{ yourTurn ? "YOUR" : "OPPONENT'S" }} turn.
    </p>
    <p v-if="waiting" class="waiting-for-opponent">Waiting for an opponent.</p>
    <p v-if="isOver" :class="youWon ? 'you-won' : 'you-lost'">
      Game over. You {{ youWon ? "won!" : "lost!" }}
    </p>
    <p v-if="opponentLeft && !isOver" class="opponent-left">
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
