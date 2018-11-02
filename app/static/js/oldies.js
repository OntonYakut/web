function getInternetExplorerVersion()
                            {
                                var rv = -1;
                                if (navigator.appName == 'Microsoft Internet Explorer')
                                {
                                    var ua = navigator.userAgent;
                                    var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
                                    if (re.exec(ua) != null)
                                        rv = parseFloat( RegExp.$1 );
                                }
                                else if (navigator.appName == 'Netscape')
                                {
                                    var ua = navigator.userAgent;
                                    var re  = new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})");
                                    if (re.exec(ua) != null)
                                        rv = parseFloat( RegExp.$1 );
                                }
                                return rv;
                            }
                            
if(getInternetExplorerVersion()!==-1){

document.write('<div id="oldies-bar" style="z-index: 65535; background: #ffffe1  no-repeat 7px 2px; border-bottom: 1px solid #716f64; border-top: 1px solid #e0dfd0; padding: 0; margin: 0; position: fixed; width:100%; height: 21px; left:0; top:0; _position: absolute; _top: expression(eval(document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop)); _left: expression(eval(document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft)); _width: expression(eval(document.documentElement.clientWidth ? document.documentElement.clientWidth : document.body.clientWidth));"><span style="display: block; float: right; padding: 2px 7px 2px 7px; margin: 0; cursor: pointer; font: 12px Verdana; color: #536482;" onclick="document.getElementById(\'oldies-shadow\').style.display=\'none\'; document.getElementById(\'oldies-bar\').style.display=\'none\';">×</span>  Внимание! Internet Explorer не умеет корректно отображать информацию на этом сайте. Для корректного отображения информации, смените браузер.</div><div id="oldies-shadow" style="height: 22px; padding: 0; margin: 0;"></div>');
}



