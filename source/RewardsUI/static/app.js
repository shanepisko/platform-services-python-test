console.log('something from the app.js')



// DEFINE COMPONENT FOR LOADING REWARDS TIERS
Vue.component('app-rewards', {
  data: function () {
    return {
      rewards: []
    }
  },
  mounted () {
    axios.get("http://localhost:7050/rewards")
      .then(response => {
        console.log('res', response.data);
        rewards = response.data;
        this.rewards = response.data;
        console.log(rewards, this.rewards)
      });
  },
  template: `
    <table class="table table-striped" border="1">

        <thead>
          <tr>
              <th>Rewards Tier</th>
              <th>Reward Points</th>
              <th>Rewards Tier Name</th>
          </tr>
        </thead>
      <tbody>
        <tr v-for="reward in rewards">
          <td>
            {{ reward.tier }}
          </td>
          <td>
            {{ reward.points }}
          </td>
          <td>
            {{ reward.rewardName }}
          </td>
        </tr>
      </tbody>

    </table>
  `
});

Vue.component('app-add-order', {
  props: {
    reloadUsers: Function,
  },
  data: function () {
    return {
      order: {
        email: '',
        total: null
      },
      emailWarning: '',
      totalWarning: '',
      successMessage: false
    }
  },
  methods: {
    handleSubmit(e) {
      e.preventDefault();
      this.successMessage = false;
      if ( this.order.email == '' ) {
        this.emailWarning = 'Email is required';
      } else {
        this.emailWarning = null;
      }
      if ( this.order.total == 0 || this.order.total == null ) {
        this.totalWarning = 'Order must be greater than 0';
      } else {
        this.totalWarning = null;
      }

      console.log('what we have in the order obj', this.order);
      if ( this.order.email != '' && this.order.total > 0 ) {
        let orderForm = new FormData();
        orderForm.append("email", this.order.email);
        orderForm.append("order_total", this.order.total);
        axios.post("http://localhost:7050/user-rewards/", orderForm, { headers: {'Content-Type': 'multipart/form-data' }})
          .then(response => {
            console.log('res', response);
            if (response.status == 200) {
              console.log('success! calling user rewards load method to reload the list');
              // this.reloadUsers();
              this.$emit('reload');
              this.successMessage = true;
            }
          });
      }
    }
  },
  template: `
        <form @submit.prevent="handleSubmit" class="justify-content-center">
          <div class="form-group">
            <input type="email" name="email" placeholder="email address" v-model="order.email" class="form-control"/>

            <div v-if="emailWarning" class="alert alert-warning" role="alert">
              {{ emailWarning }}
            </div>
          </div>
          <div class="form-group">
            <input type="number" name="total" placeholder="order total" v-model="order.total" class="form-control"/>
            <div v-if="emailWarning" class="alert alert-warning" role="alert">
              {{ totalWarning }}
            </div>
          </div>

          <button type="submit" class="btn btn-primary form-control">Submit</button>
          <div v-if="successMessage" class="alert alert-success" role="alert">
            Order Successfully Added
          </div>
        </form>
    `
})

// DEFINE COMPONENT FOR LOADING REWARDS TIERS
Vue.component('app-user-rewards', {
  data: function () {
    return {
      userRewards: [],
      search: ''
    }
  },
  // mounted () {
  //   this.getUserRewards();
  // },
  methods: {
    getUserRewards() {
      axios.get("http://localhost:7050/user-rewards/")
        .then(response => {
          console.log('res', response.data);
          userRewards = response.data;
          this.userRewards = response.data;
          console.log(this.userRewards);
        });
    }
  },
  computed:
  {
      filteredUsers:function()
      {
          var self=this;
          return this.userRewards.filter(function(user){return user.email.toLowerCase().indexOf(self.search.toLowerCase())>=0;});
      }
  },
  template: `
    <div>
      <div class="row">
        <form class="col-6" autocomplete="off">
          <input type="text" autocomplete="nope" name="search" placeholder="search user" v-model="search" class="form-control"/>
        </form>
      </div>
      <table class="table table-striped" border="1">
          <thead>
          <tr>
              <th>Email Address</th>
              <th>Reward Points</th>
              <th>Reward Tier</th>
              <th>Reward Tier Name</th>
              <th>Next Reward Tier</th>
              <th>Next Reward Tier Name</th>
              <th>Next Reward Tier Progress</th>
          </tr>
          </thead>
          <tbody>
                <tr v-for="user in filteredUsers">
                    <td>{{ user.email }}</td>
                    <td>{{ user.points }}</td>
                    <td>{{ user.tier }}</td>
                    <td>{{ user.rewardName }}</td>
                    <td>{{ user.nextTier }}</td>
                    <td>{{ user.nextRewardName }}</td>
                    <td>{{ user.tierProgress | percentage }}</td>
                </tr>
          </tbody>
      </table>
    </div>
  `
});

Vue.filter('percentage', function(value, decimals) {
  if(!value) {
    value = 0;
  }

  if(!decimals) {
    decimals = 0;
  }

  value = value * 100;
  value = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
  value = value + '%';
  return value;
});

new Vue({
  el: '#app',
  methods: {
    loadUsers () {
      this.$refs.userRewardsList.getUserRewards();
    }
  },
  mounted () {
    this.loadUsers();
  },
});
