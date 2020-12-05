<template>
  <div
    v-if="shots"
    :class="[waiting ? 'disabled' : '', , yours ? 'you' : 'opponent', 'board']"
  >
    <div v-if="yours">your board</div>
    <div v-else>opponent's board</div>
    <table :class="['board-table']">
      <tbody>
        <tr v-for="(_, x) in rows" :key="x">
          <td v-for="(_, y) in cols" :key="y" class="board-cell">
            <div
              @click="
                if (!waiting && !yours && shots[x][y] == 0) {
                  makeMove({ x: x, y: y });
                }
              "
              class="board-cell-content"
            >
              &nbsp;
              <div
                :class="{
                  'ship-part': board[x][y] != 0 && shots[x][y] != 2,
                  'shot-miss': shots[x][y] == 1,
                  'shot-hit': shots[x][y] == 2,
                }"
              >
                &nbsp;
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  props: {
    rows: Number,
    cols: Number,
    board: Array,
    shots: Array,
    yours: Boolean,

    waiting: Boolean,
  },
  methods: {
    ...mapActions(["makeMove"]),
  },
};
</script>
// :class="[ // getShipClassName( // ships[board[x][y]]['length'], //
ships[board[x][y]]['orientation'] // ), // ]"
