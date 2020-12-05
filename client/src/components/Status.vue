<template>
  <div class="status-bar">
    <p v-if="!waiting && !isOver">
      It's
      <span class="green">
        {{ yourTurn ? "your" : "opponent's" }}
      </span>
      turn.
    </p>
    <p v-if="waiting" class="blinking green">Waiting for an opponent.</p>
    <p v-if="isOver">Game over. You win/lose</p>
  </div>
</template>

<script>
export default {
  props: {
    yourTurn: Boolean,
    waiting: Boolean,
    isOver: Boolean,
  },
};
</script>
