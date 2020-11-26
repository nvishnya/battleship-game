<template>
  <div class="status-bar">It's {{ yourTurn ? "your" : "your opponent's" }} turn.</div>
</template>

<script>
export default {
  props: {
    yourTurn: Boolean,
    isOver: Boolean,
  },
};
</script>
