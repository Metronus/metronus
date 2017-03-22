var vm = new Vue({
	delimiters: ['${', '}'],
	el: '#metronus-app',
	data: {
		timestamp: Date.now()
	},

	mounted:function(){
		setInterval(function() {
			this.timestamp = Date.now()
		}.bind(this), 1000)
	},
	
	computed: {
		currentTime: function () {
			var d = new Date(this.timestamp)
			var yyyy=d.getFullYear()
			var mn=d.getMonth()+1
			var dd=d.getDate()
			var hh=d.getHours()-1
			var mm=d.getMinutes()
			var ss=d.getSeconds()
			return (yyyy+'-'+mn+'-'+dd+' '+hh+':'+mm+':'+ss)
		}
	}
})

