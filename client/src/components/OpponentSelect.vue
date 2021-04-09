<template>
  <div class="opponent-select">
    <div :style="{ 'margin-bottom': '5px' }">opponent type:</div>
    <template v-if="gameId == null">
      <button
        :class="{ 'selected-opponent': friendAsOpponent == false }"
        class="button-1"
        @click="createGameWithRandomOpponent"
      >
        random
      </button>
      <button
        :class="{ 'selected-opponent': friendAsOpponent == true }"
        class="button-1"
        @click="createGameWithFriendOpponent"
      >
        friend
      </button>
    </template>
    <template v-else>
      <button class="friend-selected button-1">friend</button>
    </template>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  computed: {
    ...mapState(["gameId", "friendAsOpponent"]),
  },
  methods: {
    ...mapActions([
      "createGameWithFriendOpponent",
      "createGameWithRandomOpponent",
    ]),
  },
};
</script>