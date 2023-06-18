<template>
  <div v-if="attackEngine" class="gnss-attack-settings">
    <b-form @submit="onSubmit">
      <b-form-group
        class="align-items-center"
        :id="sensorName + '-enable-attack-group'"
        label="Enable Attack Engine:"
        :label-for="sensorName + 'enable-attack'"
        label-cols="3"
        label-size="sm"
      >
        <b-form-checkbox
          switch
          :id="sensorName + '-enable-attacks'"
          size="lg"
          v-model="attackEngine.enabled"
        ></b-form-checkbox>
      </b-form-group>

      <b-form-row>
        <div :id="sensorName + '-settings-column1'" class="col">
          <SettingEntry
            :id="sensorName + '-attack-period'"
            label="Attack Period:"
            type="number"
            placeholder="Enter the attack period."
            tooltip="The attack is applied periodically every attackPeriod seconds if positive, continuously if zero, and randomly if negative."
            :step="0.001"
            v-model="attackEngine.attackPeriod"
          />

          <SettingEntry
            :id="sensorName + '-attack-chance'"
            label="Attack Chance:"
            type="number"
            placeholder="Enter the attack chance."
            tooltip="The attack chance if attack period is set to random."
            :step="0.01"
            :min="0"
            :max="1"
            v-model="attackEngine.attackChance"
          />

          <SettingEntry
            :id="sensorName + '-message-delay'"
            label="Message Delay [s]:"
            type="number"
            placeholder="Enter the message delay."
            tooltip="The amount of seconds by which the sensor messages are delayed."
            :step="0.001"
            v-model="attackEngine.messageDelay"
          />

          <SettingEntry
            :id="sensorName + '-offset-lat'"
            label="Offset Latitude [m]:"
            type="number"
            placeholder="Enter the latitude offset."
            tooltip="The constant offset in latitude in meters."
            :step="0.001"
            v-model="offsetLat"
          />

          <SettingEntry
            :id="sensorName + '-offset-lon'"
            label="Offset Longitude [m]:"
            type="number"
            placeholder="Enter the longitude offset."
            tooltip="The constant offset in longitude in meters."
            :step="0.001"
            v-model="offsetLon"
          />

          <SettingEntry
            :id="sensorName + '-offset-alt'"
            label="Offset Altitude [m]:"
            type="number"
            placeholder="Enter the altitude offset."
            tooltip="The constant offset in altitude in meters."
            :step="0.001"
            v-model="attackEngine.offsetValue.alt"
          />
        </div>
        <div :id="sensorName + '-settings-column2'" class="col">
          <SettingEntry
            :id="sensorName + '-spoofed-lat'"
            label="Spoofed Latitude [°]:"
            type="number"
            placeholder="Enter the spoofed latitude position."
            tooltip="The spoofed latitude position in degree."
            :step="0.001"
            v-model="attackEngine.spoofedValue.lat"
          />

          <SettingEntry
            :id="sensorName + '-spoofed-lon'"
            label="Spoofed Longitude [°]:"
            type="number"
            placeholder="Enter the spoofed longitude position."
            tooltip="The spoofed longitude position in degree."
            :step="0.001"
            v-model="attackEngine.spoofedValue.lon"
          />

          <SettingEntry
            :id="sensorName + '-spoofed-alt'"
            label="Spoofed Altitude [m]:"
            type="number"
            placeholder="Enter the spoofed altitude position."
            tooltip="The spoofed altitude position in meters."
            :step="0.001"
            v-model="attackEngine.spoofedValue.alt"
          />

          <b-form-group
            label="Active Attacks:"
            :label-for="sensorName + 'active-attacks'"
            label-cols="3"
            label-size="sm"
            v-slot="{ ariaDescribedby }"
          >
            <b-form-checkbox-group
              :id="sensorName + '-active-attacks'"
              v-model="activeAttacks"
              size="sm"
              :options="availableAttacksLabels"
              :aria-describedby="ariaDescribedby"
              buttons
            ></b-form-checkbox-group>
          </b-form-group>
        </div>
      </b-form-row>

      <div class="text-center p-4">
        <b-button type="submit" variant="primary" size="sm" class="m-2">Apply</b-button>
      </div>
    </b-form>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";
import SettingEntry from "@/components/SettingEntry.vue";

export default {
  name: "AttackSettings",
  components: { SettingEntry },
  props: {
    sensorName: String,
    attackEngine: Object,
    url: String,
  },
  data() {
    return {
      availableAttacks: [
        { id: 0, label: "No Data" },
        { id: 1, label: "No Update" },
        { id: 2, label: "Spoofed Value" },
        { id: 3, label: "Constant Offset" },
        { id: 4, label: "Delay Message" },
      ],

      // attackEngine: {
      //   enabled: true,
      //   attackPeriod: 1.0,
      //   attackChance: 0.0,
      //   messageDelay: 0.0,
      //   activeAttacks: 0,
      // },
    };
  },
  computed: {
    availableAttacksLabels: {
      get: function () {
        let labels = [];
        this.availableAttacks.forEach((attack) => {
          labels.push(attack.label);
        });
        return labels;
      },
    },
    activeAttacks: {
      // getter
      get: function () {
        let attacks = [];
        this.availableAttacks.forEach((attack) => {
          if ((this.attackEngine.activeAttacks >>> attack.id) & 0x01)
            attacks.push(attack.label);
        });
        return attacks;
      },
      // setter
      set: function (activeAttacksLabels) {
        this.attackEngine.activeAttacks = 0;
        activeAttacksLabels.forEach((label) => {
          let attack = this.availableAttacks.filter((a) => a.label === label);
          if (attack) {
            this.attackEngine.activeAttacks += Math.pow(2, attack[0].id);
          }
        });
      },
    },
    offsetLon: {
      get() {
        return Number(
          (this.attackEngine.offsetValue.lon * 60 * 1852).toFixed(3)
        ); // degree -> m
      },
      set(value) {
        this.attackEngine.offsetValue.lon = value / (60 * 1852).toFixed(3); // m -> degree
      },
    },
    offsetLat: {
      get() {
        return Number(
          (this.attackEngine.offsetValue.lat * -1 * 60 * 1852).toFixed(3)
        ); // degree -> m (negative because north directs towards -y)
      },
      set(value) {
        this.attackEngine.offsetValue.lat = value / (-1 * 60 * 1852).toFixed(3); // m -> degree (negative because north directs towards -y)
      },
    },
  },
  methods: {
    onSubmit(event) {
      event.preventDefault();

      axios({
        method: "POST",
        url: this.url,
        data: {
          attackEngine: this.attackEngine,
        },
        headers: { "content-type": "application/json" },
      }).then(
        (result) => {
          this.response = result.data;
          //   console.log(this.response);
        },
        (error) => {
          console.error(error);
        }
      );
    },
  },
};
</script>

<style scoped>
</style>
