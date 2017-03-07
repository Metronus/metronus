switch (lang = 'en') {
  case 'en':
    requiredField = 'Field required'
    passLength = 'Length should be 5 to 25'
    break
  default:
    requiredField = 'Campo obligatorio'
    passLength = 'Longitud permitida entre 5 y 20'
    break
}


var vm = new Vue({
	delimiters: ['${', '}'],
	el: '#metronus-app',
	data: {
		timestamp: Date.now(),
        ruleForm: {
          name: '',
          surname: '',
          email: '',
          phone: '',
          password: ''
        },
        rules: {
          name: [
            { required: true, message: requiredField, trigger: 'blur' }
          ],
          surname: [
            { required: true, message: requiredField, trigger: 'blur' }
          ],
          email: [
            { required: true, message: requiredField, trigger: 'blur' }
          ],
          phone: [
            { required: true, message: requiredField, trigger: 'blur' }
          ],
          password: [
            { required: true, message: requiredField, trigger: 'blur' },
            { min: 5, max: 25, message: passLength, trigger: 'blur' }
          ]
        }
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
	},
	methods: {
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (valid) {
          	// Hacer POST al backend
            console.log('Hacer POST al backend')
          } else {
            return false
          }
        });
      },
      resetForm(formName) {
        this.$refs[formName].resetFields()
      }
    }
})

