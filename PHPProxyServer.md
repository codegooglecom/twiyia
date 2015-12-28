推呀网站代理节点PHP服务器版
  * 本软件为推呀网站web代理软件,同时也可做为加速器中间结点PHP版本
  * 本软件可直接做为web代理网站使用, 也可做为推呀网站代理加速器中间
  * 如做为中间结点,请修改index.php文件, 设置 $protect = false, $cacheTime = 0
  * 此软件所在的服务器需可访问http://twiyia.com, 否则请修改index.php中的配置 $proxy\_name 和 $proxy\_ip
  * 本软件运行环境为 apache + php + URL rewrite
  * 此软件需运行于网站的根目录
  * 请保证cache目录可写
  * 注意一定上传.htaccess文件
  * 如果页面不正常,可以尝试删除缓存目录cache, 手动刷新缓存
  * 本程序为开源软件, 你可下载并查看源码, 网址 https://code.google.com/p/twiyia/
  * 本程序及源码以 GNU General Public License 方式授权发布, 参见 http://www.gnu.org/licenses/gpl.html