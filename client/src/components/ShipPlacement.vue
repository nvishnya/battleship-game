<template>
  <div v-if="field" class="field">
    <table class="field-table">
      <tbody>
        <tr v-for="(_, row) in rows" :key="row">
          <td v-for="(_, col) in cols" :key="col" class="field-cell">
            <div
              @drop="onDrop($event, row, col)"
              @dragenter.prevent
              @dragover.prevent
              class="field-cell-content"
            >
              &nbsp;
              <div
                v-if="field[row][col] != -1"
                draggable="true"
                @dragstart="startDrag($event, field[row][col])"
                :class="[
                  getShipClassName(
                    ships[field[row][col]]['length'],
                    ships[field[row][col]]['orientation']
                  ),
                ]"
              ></div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { zeros } from "../helpers";
export default {
  data() {
    return {
      // disable drag-n-drop if ships has been placed
      // placed: false,
      ships: [],
    };
  },
  props: {
    rows: Number,
    cols: Number,
  },
  created() {
    this.getRandomlyPositionedShips();
  },
  computed: {
    field() {
      console.log("update");
      let field = zeros(this.rows, this.cols);
      for (let i = 0; i < this.ships.length; i++) {
        field[this.ships[i].x][this.ships[i].y] = i;
      }
      return field;
    },
  },
  methods: {
    getShipClassName(length, orientation) {
      return `ship-${orientation}-${length}`;
    },
    async getRandomlyPositionedShips() {
      const response = await this.axios.get(
        `random-board/?rows=${this.rows}&cols=${this.cols}`
      );
      this.ships = response.data;
    },
    startDrag(evt, index) {
      var rect = evt.path[1].getBoundingClientRect();
      var docEl = document.documentElement;

      var rectTop = rect.top + window.pageYOffset - docEl.clientTop;
      var rectLeft = rect.left + window.pageXOffset - docEl.clientLeft;

      let width = evt.path[1].clientWidth;
      let height = evt.path[1].clientHeight;

      let offset_col = (evt.clientX - rectLeft) / width;
      let offset_row = (evt.clientY - rectTop) / height;

      evt.dataTransfer.dropEffect = "move";
      evt.dataTransfer.effectAllowed = "move";

      evt.dataTransfer.setData("index", index);
      evt.dataTransfer.setData("offset_row", Math.floor(offset_row));
      evt.dataTransfer.setData("offset_col", Math.floor(offset_col));
    },
    onDrop(evt, row, col) {
      console.log(evt);
      let index = evt.dataTransfer.getData("index");
      let offset_row = parseInt(evt.dataTransfer.getData("offset_row"));
      let offset_col = parseInt(evt.dataTransfer.getData("offset_col"));

      // check if placement's possible

      let newShipData = this.ships[index];
      newShipData.x = row - offset_row;
      newShipData.y = col - offset_col;

      this.$set(this.ships, index, newShipData);
    },
  },
};
</script>


<style lang="scss">
// $base-color: #036;
$cell-size: 30px;
$cell-border: 1px;

$orientations: "HR", "VR";

@for $length from 1 through 5 {
  @each $orientation in $orientations {
    .ship-#{$orientation}-#{$length} {
      z-index: 2;
      position: absolute;

      $lw: if($orientation== "HR", $length, 1);
      $lh: if($orientation== "VR", $length, 1);

      width: $cell-size * $lw + $cell-border * $lw;
      height: $cell-size * $lh + $cell-border * $lh;
      background: rgba(140, 0, 255, 0.226);
    }
  }
}
.field-table {
  user-select: none; //TODO use different properties for different browsers
  border-collapse: collapse;
  padding: 0;
}
.field-cell-content {
  width: $cell-size;
  height: $cell-size;
  // background-color: indigo;
}
.field-cell {
  border: $cell-border solid grey;
  padding: 0;
}
</style>