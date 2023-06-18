<template>
  <div class="setting-entry">
    <b-form-group
      :id="this.id + 'group'"
      :label="label"
      :label-for="this.id"
      label-cols="6"
      label-size="sm"
    >
      <b-tooltip
        :target="this.id"
        placement="auto"
        triggers="hover"
        delay="400"
        >{{ tooltip }}</b-tooltip
      >

      <b-form-input
        v-if="type === 'number'"
        :id="this.id"
        v-model="inputVal"
        size="sm"
        :type="type"
        :step="step"
        :min="min"
        :max="max"
        :placeholder="placeholder"
        number
        required
      ></b-form-input>

      <b-form-input
        v-else
        :id="this.id"
        v-model="inputVal"
        size="sm"
        :type="type"
        :step="step"
        :min="min"
        :max="max"
        :placeholder="placeholder"
        required
      ></b-form-input>
    </b-form-group>
  </div>
</template>

<script>
export default {
  name: "SettingEntry",
  computed: {
    inputVal: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit("input", val);
      },
    },
  },
  props: {
    value: null, // value can have any type
    id: String,
    type: String,
    label: String,
    placeholder: String,
    tooltip: String,
    step: Number,
    min: Number,
    max: Number,
  },
};
</script>
