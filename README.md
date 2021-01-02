# PKUCourseDataBackEnd
by aufeas

使用nginx解决跨域问题。

开启nginx
# 开启nginx
cd nginx
start nginx
前端
修改main.js，为请求加上/apis前缀，这样发出的所有请求都会在开头加上apis（可以看我的github上的main.js，在userprofile分支里）：

import axios from './axios'
Vue.prototype.$axios = axios
axios.defaults.baseURL = '/apis'
打包：

npm run build
将dist里的东西复制到nginx/html（我已经复制过了，有修改的话自己手动复制一下）：

image-20210101201012388

直接在浏览器输入localhost即可访问（不需要端口号）。

image-20210101201101838

我这里是把/重定向到了/login，而且刷新后页面不会丢失。

如果有修改，重新build并复制到html文件夹。

后端
# 运行django
python manage.py runserver
nginx会把请求转发到后端。

后端可以实时修改。
