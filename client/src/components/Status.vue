<template>
  <div class="status-bar">
    <p v-if="!waiting && !isOver && !opponentLeft">
      It's
      <span class="green">
        {{ yourTurn ? "your" : "opponent's" }}
      </span>
      turn.
    </p>
    <p v-if="waiting" class="blinking green">Waiting for an opponent.</p>
    <p v-if="isOver">
      Game over.
      <span :class="youWon ? 'green' : 'red'">
        You {{ youWon ? "won!" : "lost!" }}
      </span>
    </p>
    <p v-if="opponentLeft" class="red">
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
    ...mapState(["shipsPlaced", "gameStarted", "yourTurn", "isOver", "youWon", "opponentLeft"]),
  },
};
</script>
