<template>
  <div class="modal-wrapper">
    <div class="modal">
      <div class="modal-body">
        <div>Sorry, this game is unavailable.</div>
        <button @click="resetGame" class="modal-button">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  methods: {
    ...mapActions(["resetGame"])
  }
};
</script>
