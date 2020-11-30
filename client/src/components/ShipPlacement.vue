<template>
  <div>
    <div v-if="board" class="board">
      <table class="board-table">
        <tbody>
          <tr v-for="(_, row) in rows" :key="row">
            <td v-for="(_, col) in cols" :key="col" class="board-cell">
              <div
                class="board-cell-content"
                @drop="onDrop($event, row, col)"
                @dragenter.prevent
                @dragover.prevent
              >
                &nbsp;
                <div
                  v-if="board[row][col] != -1"
                  :class="[
                    getShipClassName(
                      ships[board[row][col]]['length'],
                      ships[board[row][col]]['orientation']
                    ),
                  ]"
                  draggable="true"
                  @dragstart="onDragStart($event, board[row][col])"
                  @dblclick="rotate($event, board[row][col])"
                ></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- <div class="clues">
      * double click to rotate * drag and drop to move
    </div> -->
    <div>
      <button class="btn" @click="randomizeShips">randomize</button>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { isPlacementPossible, placeShips, zeros } from "../helpers";
export default {
  props: {
    rows: Number,
    cols: Number,
  },
  computed: {
    ...mapState(["ships"]),
    board() {
      let board = zeros(this.rows, this.cols, -1);
      for (let i = 0; i < this.ships.length; i++) {
        board[this.ships[i].x][this.ships[i].y] = i;
      }
      return board;
    },
  },
  methods: {
    ...mapActions(["randomizeShips"]),
    getShipClassName(length, orientation) {
      return `ship-${orientation}-${length}`;
    },
    onDragStart(event, shipIndex) {
      event.dataTransfer.dropEffect = "move";
      event.dataTransfer.effectAllowed = "move";

      let size = event.path[2].clientWidth; // + clientTop / + clientLeft

      let offsetRow = Math.floor(event.offsetY / size);
      let offsetCol = Math.floor(event.offsetX / size);

      event.dataTransfer.setData("shipIndex", shipIndex);
      event.dataTransfer.setData("offsetRow", offsetRow);
      event.dataTransfer.setData("offsetCol", offsetCol);
    },
    onDrop(event, x, y) {
      let shipIndex = event.dataTransfer.getData("shipIndex");
      let offsetX = parseInt(event.dataTransfer.getData("offsetRow"));
      let offsetY = parseInt(event.dataTransfer.getData("offsetCol"));

      let newX = x - offsetX;
      let newY = y - offsetY;

      let ship = JSON.parse(JSON.stringify(this.ships[shipIndex]));
      ship.x = newX;
      ship.y = newY;

      let tempShips = this.ships.filter(function (_, index) {
        return index != shipIndex;
      });
      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.$set(this.ships, shipIndex, ship);
      }
    },
    rotate(event, shipIndex) {
      let ship = JSON.parse(JSON.stringify(this.ships[shipIndex]));
      ship.rows = this.ships[shipIndex].cols;
      ship.cols = this.ships[shipIndex].rows;
      ship.orientation =
        this.ships[shipIndex].orientation == "HR" ? "VR" : "HR";

      let tempShips = this.ships.filter(function (_, index) {
        return index != shipIndex;
      });
      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.$set(this.ships, shipIndex, ship);
      }
    },
  },
};
</script>
