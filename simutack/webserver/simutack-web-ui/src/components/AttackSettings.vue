<template>
  <div v-if="attackEngine" class="attack-settings">
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
        tooltip="The attack is applied periodically every attack_period s if positive, continuously if zero, and randomly if negative."
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
        </div>
        <div :id="sensorName + '-settings-column2'" class="col">

      <SettingEntry
        :id="sensorName + '-message-delay'"
        label="Message Delay [s]:"
        type="number"
        placeholder="Enter the message delay."
        tooltip="The amount of seconds by which the sensor messages are delayed."
        :step="0.001"
        v-model="attackEngine.messageDelay"
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
        <b-button type="submit" variant="primary"  size="sm" class="m-2">Apply</b-button>
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
        { id: 5, label: "Camera Blinding" },
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
          console.log(this.response);
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
