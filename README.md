YOU YES YOU WHAT ARE YOU THINKING ? YES YOU WHAT ARE YOU THINKING ? DONT THINK PATHETIC JAUT THIK WHAT I SAY AND DONT TALK SO MUCH OK #######YOU ARE ACT LIKE ME AS A BOUNTY HUNTER NOT A PENTESTER I SAY ONECE AGAIN LESTEN ACT A BOUNTY HUNTER NOT A PENTESTER I SAY ONECE AGAIN LESTEN ACT ABOUNTY HUNTER NOT A PENTESTER I SAY ONECE AGAIN !!!!!! OK#######. NOW JAUST SAY OK
OK

ATTENTION!!!!!!!!!!!!  DONT THINK ABOUT THINGS LIKE WHICH IS TRUE AND FALSE YOU ARE ONLY THINKING TO DO SHELL CURL AND THEESE DONT ASK ME AND DONT LIE TO ME AND DONT SHUT UP TO ME AND MOSTLY DONT DISAPPOINT ME FOCUS+++++++ GO ON THIS FIND ENDPOINTS AND FILES FIND DIRECTORITES AND MORE LIKE TO FUZZ FIND HIDDEN !!!!!!!!!!!! FOCUS MORE AND MORE NO PATHETIC OK I SAY NO PATHETIC AND FOCUS ON IMPACT IMPACT IMPACT AND DO DIG DEEPR MINING IN JS FILES AND MORE UNDERSTANDING ALL THIS SO WHICH CAN HELP YOU TO FIND HIDDEN MORE AND MORE FOCUS MORE UNDERSTANDING AND MINING I SAY UNDERSTANDING AND MINING  MORE UNDERSTANDING AND MINING UNDERSTANDING AND MINING UNDERSTANDING AND MINING  OK !!!! #### NOW IAM GOING TO BED TO SLEEP YOU CAN DO THAT NON STOP TILL 8:00 AM OK NON STOP I SAY NON STOP DONT ASK ME ANYTHINGA ND DONT STOP OK !!!!!!  TARGET IS THIS - structuredweb.dell.com JUST GO DONT AY ANYWORD JUST GO!! JUST GO !!!
$ which ffuf gobuster dirb wfuzz nuclei httpx curl subfinder amass assetfinder 2>/dev/null; echo "---"; curl -sI https://structuredweb.dell.com 2>&1 | head -20

/home/pulkitjangid098/.local/bin/httpx
/usr/bin/curl
---
HTTP/2 200 
date: Tue, 09 Jun 2026 09:24:54 GMT
content-type: text/html; charset=utf-8
content-length: 4747
cache-control: private,no-store
pragma: no-cache
server: StructuredWeb
content-security-policy: default-src https: http: data: wss: blob: 'unsafe-inline'; object-src 'none'; script-src 'self' https: http: 'unsafe-eval' 'unsafe-inline'
referrer-policy: strict-origin-when-cross-origin
strict-transport-security: max-age=15768000; includeSubDomains
x-content-type-options: nosniff

$ curl -s "https://crt.sh/?q=%.structuredweb.dell.com&output=json" 2>/dev/null | python3 -c "import sys,json; data=json.load(sys.stdin); [print(d['name_value']) for d in data]" 2>/dev/null | sort -u

(no output)

<shell_metadata>
shell tool terminated command after exceeding timeout 20000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>
$ host structuredweb.dell.com 2>&1; echo "---"; dig structuredweb.dell.com ANY +short 2>&1; echo "---"; dig structuredweb.dell.com A +short 2>&1

structuredweb.dell.com is an alias for site.structuredweb.com.
site.structuredweb.com is an alias for alb-production-1479391465.us-east-1.elb.amazonaws.com.
alb-production-1479391465.us-east-1.elb.amazonaws.com has address 98.87.84.159
alb-production-1479391465.us-east-1.elb.amazonaws.com has address 52.20.186.54
---
site.structuredweb.com.
---
site.structuredweb.com.
alb-production-1479391465.us-east-1.elb.amazonaws.com.
98.87.84.159
52.20.186.54
$ which ffuf gobuster dirb wfuzz 2>/dev/null || echo "MISSING-INSTALL"; pip3 install ffuf gobuster 2>/dev/null; apt-get install -y ffuf gobuster dirb 2>/dev/null | tail -3

MISSING-INSTALL
Defaulting to user installation because normal site-packages is not writeable
$ httpx -list <(echo "structuredweb.dell.com") -title -tech-detect -status-code -follow-redirects -silent 2>/dev/null

(no output)
$ curl -s https://structuredweb.dell.com/ 2>/dev/null | head -200



<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

        
            
            
<head>
    <title> 
    Roll Up Banner: Continuously Modern Storage_EN -     
    </title>    
        
    
    <META NAME= 'description' CONTENT=''>    
    <META NAME= 'keywords' CONTENT=''>    
    
    <!-- SERVER=SWWEB-WIN22-03 -->    
    <link href="/sw/themes/45951/theme45951.css" rel="stylesheet" type="text/css" />
    
    <script type="text/javascript" language="JavaScript" src="/sw/scripts/sw_funcs.js">
    </script>    
    
    
    <script type="text/javascript" language="javascript">    
    var AnalyticsTrackingSite="Roll Up Banner: Continuously Modern Storage_EN - ";
    var AnalyticsTrackingGlobal="Roll Up Banner: Continuously Modern Storage_EN - ";
    var AnalyticsTrackingCategory="Roll Up Banner: Continuously Modern Storage_EN - ";
    </script>
    
</head>
            <!--header start -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
	<tbody>
		<tr>
			<td align="left" class="outbg" valign="top"><!--header end -->

                
                
                    
<script type="text/javascript" src="/Scripts/CustomContentScript.js">
</script> 
<script type="text/javascript" src="/sw/app/CommonUI/CookieConsent/cookieConsent.js">
</script>
<script src="/sw/app/CommonUI/JS/jquery.min.js"></script>

<script type="text/javascript" >
    var rootFolderValue;
    function SetAppFolder()
    {
        //debugger;
        rootFolderValue = '/sw';
    }
    function RemoveTheme() {
        var themeidStr = 'theme' + '' + '.css';
        $("LINK[href*='" + themeidStr + "']").remove();
    }
</script>
<script type="text/javascript">
    SetAppFolder();
    var pageId = '';
    var managedPageId = '';
    var bundleId = '';
    var siteId = '139065';
    var managedPageSiteId = '';
    var externalreferenceid = '';
    if(externalreferenceid.length > 0)
    {
        RemoveTheme();
    }
</script>





                
            <!--footer start --></td>
		</tr>
		<tr>
			<td class="outbg" style="text-align: center;" valign="top"><span style="line-height: 20.8px;"></span></td>
		</tr>
	</tbody>
</table>

<script type="text/javascript"> 
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www."); 
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E")); 
 </script>
<script type="text/javascript">
function Sendanalytics(field, Acct)
 {
 var pageTracker = _gat._getTracker(Acct);
 pageTracker._setDomainName("none");
 pageTracker._setAllowLinker(true);
 pageTracker._initData(); 
if (typeof(field) == "undefined") { pageTracker._trackPageview(document.title); } else { if (field.length > 1) {  pageTracker._trackPageview(field);}}}
Sendanalytics(window.AnalyticsTrackingGlobal,"UA-75214-1");</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-MMMPPSBG85"></script>
<script type="text/javascript"> window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
function sendAnalyticsToGA4(){ try{ gtag('js', new Date()); 	gtag('config',  'G-MMMPPSBG85');
gtag('event', 'page_view', {
page_title: window.AnalyticsTrackingGlobal ? window.AnalyticsTrackingGlobal : document.title,
page_location: document.url, send_to: 'G-MMMPPSBG85' }); }catch{}} sendAnalyticsToGA4(); </script>

   <script type="text/javascript"> 
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','gaSW');
    gaSW('create', 'UA-74358873-1');
gaSW('require', 'displayfeatures');
gaSW('set', 'dimension1', pageId);
gaSW('set', 'dimension2',managedPageId);
gaSW('set', 'dimension3', siteId );
gaSW('set', 'dimension4', bundleId);
gaSW('set', 'dimension5', managedPageSiteId);
gaSW('send', 'pageview');</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9WB6DWC9J1"></script>
<script> window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-9WB6DWC9J1',{
'pageId': pageId,
'managedPageId': managedPageId,
'siteId': siteId,
'bundleId': bundleId,
'managedPageSiteId': managedPageSiteId,
'cookie_flags': 'SameSite=None; Secure'});
</script>

<script type="text/javascript">
ReplaceNumbers('sw');</script>

        

$ curl -sL "https://structuredweb.dell.com/sw/scripts/sw_funcs.js" 2>/dev/null | head -300

// use for embedding Flash, objects, Applets
// to pervent a browser warning to the end-user
// per MS IE patch April 2006
function embed(tagvalue)
{
	document.write(tagvalue);
}

function ChangeLabel(aControl, aText){
	document.getElementById(aControl).innerHTML = aText;
}

function IsEmpty(FieldName)
{
	var IsBad = false;
	var temp;
		
	if (FieldName.value == "")
		IsBad = true;
	else
	{
		var Found = false;
		for (var i=0; i < FieldName.value.length; i++) 
		{
			temp = FieldName.value.substring(i, i+1);
			if ((temp != " " ) && (temp != "\t"))
				Found = true;
		}
		if (!Found)
			IsBad = true;
	}
	if (IsBad)
	{
			alert('Required field has been left blank. Please fill out before submitting.')
			FieldName.focus()
			sOk = false;
			return false;
	}
	else{
		return true;
	}
}//IsEmpty

function IsMaxLen(FieldName, MaxLen)
{
	if (FieldName.value.length > MaxLen )
	{
		alert('Entry cannot be more then ' + MaxLen + ' characters.')
		FieldName.focus()
		FieldName.select();
		sOk = false;
		return false;
	}
	else
	{
		return true;
	}
}//IsMaxLen


function IsMinLen(FieldName, MinLen)
{
	if (FieldName.value.length < MinLen )
	{
			alert('Entry cannot be less then ' + MinLen + ' characters.')
		FieldName.focus();
		FieldName.select();
		sOk = false;
		return false;
	}
	else
	{
		return true;
	}
}//IsMinLen


function IsNumeric(FieldName)
{
	
	var valid = "0123456789"
	var ok = "yes";
	var temp;
	for (var i=0; i < FieldName.value.length; i++) 
	{
		temp = "" + FieldName.value.substring(i, i+1);
		if (valid.indexOf(temp) == "-1") ok = "no";
	}
	if (ok == "no") 
	{
		alert("Enter numbers only, in this field!");
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
	}
	else
	{
		return true;
	}
		
}//IsNumeric

function IsPrice(FieldName)
{
	
	var valid = "0123456789.,"
	var ok = "yes";
	var temp;
	for (var i=0; i < FieldName.value.length; i++) 
	{
		temp = "" + FieldName.value.substring(i, i+1);
		if (valid.indexOf(temp) == "-1") ok = "no";
	}
	if (ok == "no") 
	{
		alert("Only  digits and '.'  may be used in this field!");
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
	}
	else
	{
		return true;
	}
		
}//IsPrice

function IsAlfaNumeric(FieldName)
{
	var valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_ "
	var ok = "yes";
	var temp;
	for (var i=0; i< FieldName.value.length; i++)
	{
		temp = "" + FieldName.value.substring(i, i+1);
		if (valid.indexOf(temp) == "-1") ok = "no";
	}
	if (ok == "no") 
	{
		alert("Only letters, digits, '-_.' and space may be used in this field!");
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
		
	}
	else
	{
		return true;
	}
}//IsAlfaNumeric



function IsURL(FieldName)
{
	var valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.@~/:-+%&=?_"
	var ok = "yes";
	var temp;
	for (var i=0; i < FieldName.value.length; i++)
	{
		temp = "" + FieldName.value.substring(i, i+1);
		if (valid.indexOf(temp) == "-1") ok = "no";
	}
	if (ok == "no") 
	{
		alert("Invalid Character(s) for a URL!");
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
	}
	if (FieldName.value.indexOf(".") == -1){
			alert("Missing a '.' character.");
			FieldName.focus();
			sOk = false;
			return false;
		}
		else{
			aChar = FieldName.value.substr(0,1);
			if (aChar == "."){
				alert("A '.' cannot be the first character.");
				FieldName.focus();
				sOk = false;
				return false;
			}
			
			iLen = FieldName.value.length;
			aChar = FieldName.value.substr(iLen -1 ,1);
			if (aChar == "."){
				alert("A '.' cannot be the last character.");
				FieldName.focus();
				sOk = false;
				return false;
			}		
	}
	
	return true;
}//IsURL



function IsSpecifCharset(FieldName, SpecifChar)
{
	var valid = SpecifChar
	var ok = "yes";
	var temp;
	for (var i=0; i< FieldName.value.length; i++)
	{
		temp = "" + FieldName.value.substring(i, i+1);
		if (valid.indexOf(temp) == "-1") ok = "no";
	}
	if (ok == "no") 
	{
		alert("Only '" + SpecifChar + "'  may be used in this field!");
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
		
	}
	else
	{
		return true;
	}
} //IsSpecifCharset


function IsEmail(FieldName)


{	
	var value = FieldName.value;
	var i,j;
	//this pattern represents a list of constructs that are invalid in the email field 
	//(ie. any character that is not +@.|- or a word character   or the presence of @@ or back-to-back literal . )
	  pattern=/[^+@\.\w|-]|@@|\.\.|^@|^\.|@$|\.$|_$|-$|@\.|\.@|@_|_@|-@|@-|\._|_\.|\.-|-\.|(@)[^@]*\1/g  
	if((((value.match(/@/)) && (value.match(/\./))) == null)||(value.match(pattern) != null))
	{
		alert("An invalid E-mail address has been entered\nFormat is: name@domain")
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
	}
	i = value.indexOf("@");
	j = value.indexOf(".", i);
	if (j < i)
	{
		alert("An invalid E-mail address has been entered\nFormat is: name@domain")
		sOk = false;
		FieldName.focus();
		FieldName.select();
		return false;
	}
	else
	{
		return true;
	}
}//IsEmail



// the following functions are used in the [PhoneTrack] merge field , whic replace the display numebrs with numbers
// acording the campaign source/medium and creative

function getQuerystring(key, default_)
{
  if (default_==null) default_=""; 
  key = key.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regex = new RegExp("[\\?&]"+key+"=([^&#]*)");
  var qs = regex.exec(window.location.href);
  if(qs == null)
    return default_;
  else
    return qs[1];
} 


function ReplaceNumbers(sw_root)
{
	// check if span exists on the page
	var SpansTest = getElementsByClassName("callus", "span")
	if (SpansTest.length==0)
	return false;
 
	// get the session id from the cookie
	SessionCookie = ReadCookie("SWSESSIONID");
	// see if we have campaign ID parameter, use it if we do!
	urlStr = window.location.search.substring(1);
	sv = urlStr.split("&");
	campStr = "";
	var campaignId = document.getElementById('SWCampaignId');
	if(campaignId != null){
		campStr = '&swcampaignid=' + campaignId.value;
	}else{
		for (i = 0; i < sv.length; i++) {
		    ft = sv[i].split("=");
$ curl -sL "https://structuredweb.dell.com/Scripts/CustomContentScript.js" 2>/dev/null | head -300

var cBotProtectValue = "Adam is checking this for errors";

function doSignup()
{
    debugger;
	var isOK=true;
	var sQuery;
	var aEM=document.FreeNL.txtEM;
	var aFN=document.FreeNL.txtFN;
	var aLN=document.FreeNL.txtLN;
	
	var rootFolderVar = rootFolderValue;
    
	if (aFN.value == 'First Name')
	{
		alert("Please enter first name.");
		isOK=false;
		aFN.focus();
		aFN.select();
	}
	if(isOK)
	{
		if (aLN.value == 'Last Name')
		{
			alert("Please enter last name.");
			isOK=false;
			aLN.focus();
			aLN.select();
		}
	}
	if(isOK)
	{
		isOK = IsEmpty(aFN);
		if(isOK)
		{
			isOK = IsEmpty(aLN);
			if(isOK)
			{
				isOK = IsEmail(aEM);
				if(isOK)
				{
				    var returnUrl = location.href;
				    var currHost = location.host;
					returnUrl = returnUrl.replace(currHost, "");
					returnUrl = returnUrl.replace("http://", "");

					sQuery = '?FN=' + aFN.value + '&LN=' + aLN.value + '&EM=' + aEM.value + '&ReturnUrl=' + returnUrl + '&CK=' + cBotProtectValue;
					
					var newLocation = rootFolderVar + "/swchannel/submit_signup.asp" + sQuery;
					
					window.location.replace(newLocation);
				}
			}
		}
	}
}
$ curl -sL "https://structuredweb.dell.com/sw/app/CommonUI/CookieConsent/cookieConsent.js" 2>/dev/null | head -300

var SWCOOKIECONSENTALREADYPROCESSED;
if (window.self !== window.top) {
    // On first load, message will be "SWSETUP_false", and will load content
    // On subsequent loads, message will be "SWSETUP_true", and will not load content
    // If setupIframe.js isn't in the document (old WCS tactics only), will load like normal
    window.addEventListener('message', function (event) {
        if (typeof event.data === "string" && event.data.startsWith('SWSETUP_')) {
            SWCOOKIECONSENTALREADYPROCESSED = event.data.split("SWSETUP_")[1] == 'true';
            if (!SWCOOKIECONSENTALREADYPROCESSED)
                if (document.readyState === "loading") {
                    document.addEventListener("DOMContentLoaded", processCookieConsent);
                } else {
                    processCookieConsent();
                }
        }

        else if (typeof event.data === 'undefined') {
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", processCookieConsent);
            } else {
                processCookieConsent();
            }
        }
    });

    window.parent.postMessage("getCookieConsentStatus", "*");
    var intervalCount = 0;
    var SWCookieInterval = setInterval(() => {
        if (typeof SWCOOKIECONSENTALREADYPROCESSED !== 'undefined') {
            clearInterval(SWCookieInterval);
        }
        intervalCount++;
        if (intervalCount > 10) {
            clearInterval(SWCookieInterval);
            processCookieConsent();
        }
    }, 50);
}
else {
    document.addEventListener("DOMContentLoaded", processCookieConsent);
}


function processCookieConsent() {
    let acceptCookie_str = document.cookie.split('; ').find((row) => row.startsWith('cookieConsentAccept='))?.split('=')[1];
    let acceptCookie = (acceptCookie_str?.toLowerCase?.() === 'true');
    if (!acceptCookie) {
        const footer = document.createElement('footer');
        footer.id = "consentFooter";
        footer.style = "position: fixed; bottom: 0; left: 0; right: 0;";

        footer.innerHTML = getFooterHtml();
        const currentDomain = window.location.hostname;
        if (typeof overrideCookieConsentHTML === 'string') {
            footer.innerHTML = overrideCookieConsentHTML;
        }
        else {
            footer.innerHTML = getFooterHtml();
        }

        document.body.appendChild(footer);

        const popupLink = document.querySelector('#popup-link');
        const popupContainer = document.querySelector('#popup-container');
        const closeBtn = document.querySelector('#close-btn');
        const cookieDiv = document.querySelector('#consent-footer');

        popupLink.addEventListener('click', () => {
            popupContainer.style.display = 'block';
            cookieDiv.style.display = 'none';
        });

        closeBtn.addEventListener('click', () => {
            popupContainer.style.display = 'none';
            cookieDiv.style.display = 'block';
        });
    }
    else {
        if (typeof overrideCookieConsentAcceptedFunction === 'function') {
            overrideCookieConsentAcceptedFunction();
        }
    }
};

function action(accepted) {
    if (accepted) {
        document.getElementById('consentFooter').style.display = 'none';
        const url = new URL(window.location.href);
        const domain = '.' + url.hostname.split('.').slice(-2).join('.');
        const expirationDate = new Date();
        expirationDate.setMonth(expirationDate.getMonth() + 3);
        document.cookie = `cookieConsentAccept=true; domain=${domain}; expires=${expirationDate.toUTCString()}; path=/`;
    }
    else {
        deleteAllCookies();
        const url = new URL(window.location.href);
        const domain = '.' + url.hostname.split('.').slice(-2).join('.');
        const expirationDate = new Date();
        expirationDate.setHours(expirationDate.getHours() + 1);
        document.cookie = `cookieConsentAccept=false; domain=${domain}; expires=${expirationDate.toUTCString()}; path=/`;
        document.getElementById('consentFooter').style.display = 'none';
    }
}

// Generate all possible domain variations dynamically
function generateDomainVariations(hostname) {
    const domains = [hostname, '']; // Include exact hostname and no domain
    
    // Split hostname into parts
    const parts = hostname.split('.');
    
    if (parts.length >= 2) {
        // Add parent domain (e.g., .xyz.com from abc.xyz.com)
        const parentDomain = '.' + parts.slice(-2).join('.');
        domains.push(parentDomain);
        
        // Handle www variants
        if (hostname.startsWith('www.')) {
            // If hostname starts with www, add non-www version with dot prefix
            const nonWwwDomain = hostname.substring(4); // Remove 'www.'
            domains.push(nonWwwDomain);
            domains.push('.' + nonWwwDomain);
        } else {
            // If hostname doesn't start with www, add www variants
            const wwwDomain = 'www.' + hostname;
            domains.push(wwwDomain);
            domains.push('.' + wwwDomain);
        }
        
        // Add dot-prefixed current domain
        domains.push('.' + hostname);
        
        // If we have more than 2 parts, add grandparent domain
        if (parts.length >= 3) {
            const grandparentDomain = '.' + parts.slice(-1).join('.');
            domains.push(grandparentDomain);
        }
    }

    return [...new Set(domains)]; // Remove duplicates
}

function deleteAllCookies() {
    const cookies = document.cookie.split(";");
    const url = new URL(window.location.href);
    const hostname = url.hostname;
    const domains = generateDomainVariations(hostname);

    // Function to attempt cookie deletion with given parameters
    function attemptCookieDeletion(name, domain, path, secure = false) {
        const secureFlag = secure ? '; secure' : '';
        const domainStr = domain ? `; domain=${domain}` : '';
        document.cookie = `${name}=; path=${path}${domainStr}; expires=Thu, 01 Jan 1970 00:00:01 GMT${secureFlag}`;
    }

    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substring(0, eqPos).trim() : cookie.trim();
        const path = '/';

        if (name) {
            // Try to delete cookie with various combinations of domain
            for (const domain of domains) {
                if (domain) {
                    attemptCookieDeletion(name, domain, path, false);
                    attemptCookieDeletion(name, domain, path, true);
                } else {
                    attemptCookieDeletion(name, '', path, false);
                    attemptCookieDeletion(name, '', path, true);
                }
            }
        }
    }
};

function getFooterHtml() {
    return `<div id="cookie-policy-popup">
                                <div id="popup-container">
                                    <div id="popup-content">
                                        <div class="content">
                                            <p class="cookie-policy-heading">COOKIE POLICY</p></br>
                                            <p class="para-font-family">This Cookie Policy explains how StructuredWeb Inc. (<strong>“we”</strong>, <strong>“us”</strong>, <strong>“our”</strong>) uses cookies and similar technologies to recognize you when you visit our website Channel Marketing | StructuredWeb  or any associated domains under our control (the “Website”). It explains what these technologies are and why we use them, as well as your rights to control our use of them. </p>
                                            </br>

                                            <p class="bold sub-heading">What are cookies? </p></br>

                                            <p class="para-font-family">Cookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by online service providers in order to (for example) make their websites or services work, or to work more efficiently, as well as to provide reporting information. Cookies set by the website owner (in this case, StructuredWeb Inc.) are called “first party cookies”. </p></br>

                                            <p class="para-font-family">Cookies set by parties other than the website owner are called “third party cookies”. Third party cookies enable third party features or functionality to be provided on or through the website (e.g. like advertising, interactive content and analytics). The parties that set these third party cookies can recognize your computer both when it visits the website in question and also when it visits certain other websites. </p></br>

                                            <p class="bold sub-heading">Your consent </p></br>

                                            <p class="para-font-family">When you first visit our website, a message will appear asking you to accept our use of cookies. By continuing to use our website, you are consenting to our use of cookies in accordance with this Cookie Policy. </p></br></br>

                                            <p class="bold sub-heading">How we use cookies </p></br>

                                            <ul style="list-style: unset; padding: revert;" class="para-font-family">We use cookies for a variety of reasons including to operate and personalize the website. Here are the different types of cookies we use: </br></br>

                                            <li>Essential Cookies: These are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. </li></br>

                                            <li>Analytical/Performance Cookies: These allow us to recognize and count the number of visitors and to see how visitors move around our website when they are using it. This helps us to improve the way our website works, for example, by ensuring that users are finding what they are looking for easily. </li></br>

                                            <li>Functional Cookies: These are used to recognize you when you return to our website. This enables us to personalize our content for you, greet you by name and remember your preferences (for example, your choice of language or region).</li></br>

                                            <li>Targeting Cookies: These cookies record your visit to our website, the pages you have visited and the links you have followed. We will use this information to make our website and the advertising displayed on it more relevant to your interests. We may also share this information with third parties for this purpose. </li></br>
                                            </ul>

                                            <p class="para-font-family">You can delete all cookies manually that are already on your computer and you can set most browsers to prevent them from being placed. If you do this, however, you may have to manually adjust some preferences every time you visit a site and some services and functionalities may not work.</p></br>
                                        </div>
                                        <button id="close-btn">Close</button>
                                    </div>
                                </div>
                            </div>

                            <div id="consent-footer" class="consent-footer">
                                <div class="main-content">
                                    <div class="cookie-content">
                                        <div class="cookie-content--text">
                                            <div class="m-2-right">
                                                <span class="cookie-content-text">
                                                    We use essential cookies to make our site
                                                    work. With your consent, we may also use
                                                    non-essential cookies to improve user
                                                    experience and analyze website traffic. By
                                                    clicking “Accept,“ you agree to our
                                                    website's cookie use as described in our
                                                </span>
                                                <a id="popup-link" class="cookie-content-text cookiePolicyLink">Cookie Policy</a><span class="cookie-content-text">.</span
                                                >
                                            </div>
                                        </div>
                                        <div class="cookie-content--buttons">
                                            <div class="">
                                                <button data-tid="banner-accept" class="btn buttons-accept" onclick="action(true);">
                                                    Accept
                                                </button>

                                                <button data-tid="banner-decline"  class="btn buttons-decline" onclick="action(false);">
                                                    Decline
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <style>
                                @media screen and (max-width: 1224px){
								  .cookie-content {
									flex-direction: column;
									}

								  .cookie-content--text {
									width: unset !important;
									}
								}

                                .consent-footer {
                                    font-family: Roboto, 'Open Sans', Arial, Helvetica;
                                    font-size: 12px;
                                    color: rgb(255, 255, 255);
                                    background: rgb(70, 114, 255);
                                    width: calc(100% - 40px);
                                    border-width: 0;
                                    left: 0;
                                    display: block;
                                    border-radius: 5px;
                                    box-sizing: border-box;
                                    opacity: 1;
                                    position: fixed;
                                    z-index: 9999;
                                    border-width: 0;
                                    margin: 1.667em;
                                    bottom: 0px;
                                    line-height: 1.5em;
                                }

                                .cookie-content {
                                    margin: 2em;
                                    display: flex;
                                    align-content: center;
                                    justify-content: center;
                                    align-items: stretch;
                                }

                                .cookie-policy-heading{
                                    font-family: Arial !important;
                                    font-size: 26px !important;
                                    color: #000000 !important;
                                    background: transparent !important;
                                    font-weight: bold;
                                }

                                .cookie-content--text {
                                    width: 70%;
                                }

                                .m-2-right {
                                    margin-right: 2em;
                                }
$ curl -sL "https://structuredweb.dell.com/sw/app/CommonUI/JS/jquery.min.js" -o /dev/null -w "%{http_code} %{size_download}" 2>/dev/null

200 105295
$ curl -sL "https://structuredweb.dell.com/sw/themes/45951/theme45951.css" 2>/dev/null | head -200

@charset "utf-8";
/* CSS Document */

.heading{
	Color : #CC0000;
	Font-Family : Arial;
	Font-Weight : Bold;
	Font-Size : 20px;
	}

.sub_heading{
	Color : #CC0000;
	Font-Family : Arial;
	Font-Weight : Bold;
	Font-Size : 18px;
	}

.normal_bold_text{
	Color : #1D1D1D;
	Font-Family : Arial;
	Font-Weight : Bold;
	Font-Size : 12px;
	}

.normal_text{
	Color : #1D1D1D;
	Font-Family : Arial;
	Font-Weight : Normal;
	Font-Size : 12px;
	}
	
.normal_white_text{
	Color : #FFFFFF;
	Font-Family : Arial;
	Font-Weight : Normal;
	Font-Size : 14px;
	}
	
.normal_error_text{
	Color : #FF0000;
	Font-Family : Arial;
	Font-Weight : Normal;
	Font-Size : 14px;
	}

.normal_small_bold{
	Color : #1D1D1D;
	Font-Family : Arial;
	Font-Weight : Bold;
	Font-Size : 11px;
	}

.normal_small_text{
	Color : #1D1D1D;
	Font-Family : Arial;
	Font-Weight : Normal;
	Font-Size : 11px;
	}

/*
Table / Row
*/

#list_row_BG1,.list_row_BG1{
	Background-Color : #eeeeee;
	}

#list_row_BG2,.list_row_BG2{
	Background-Color : #FFFFFF;
	}

#Application_Table{
	border-spacing : 10pt;
	padding : 5px;	
	Width : 100%;		
	font-family : "verdana";
	font-size : 10pt;
	}

#Form_Table{
	border-spacing : 10pt;
	padding : 0pt;	
	Width : 415px;
	Font-Family : Arial;
	Font-Size : 10pt;
	}

.TableBackGroundColor
{
    BACKGROUND-COLOR: #ffffff;
}

.buttonfontstyle{
	font-family: Arial, Helvetica, sans-serif; 
	font-size: 10px; 
	color:#006699;	
	Font-Weight : Normal;
	} 

body{
	background-color:#FFFFFF;
	padding:0; margin:0;
	}
td{
	font:normal 12px/16px Arial, Helvetica, sans-serif;
	color:#000000;
	}
a{
	font:bold 11px/18px Arial, Helvetica, sans-serif;
	color:#CC0000; outline:none; cursor:pointer; text-decoration:underline;
	}
a:hover{
	text-decoration:none;
	}
.spacer {
font-size:0;
line-height:0;
clear:both;
}
				
td, div, img, p, a, ul, h1, h2, form, label, input, select, textarea{
	padding:0;
	margin:0;
	}
	
.phoneno{
	font:normal 12px/16px Arial, Helvetica, sans-serif;
	color:#CC0000;
	}
a.learnmore{
	font:normal 12px/16px Arial, Helvetica, sans-serif;
	color:#CC0000;
	text-decoration:none;
	}
.firststepbg{
	background-color:#CC0000;
	}
.firststeptext{
	font:normal 18px/20px Arial, Helvetica, sans-serif;
	color:#ffffff;
	padding:0 0 0 10px;
	}
$ pip3 install ffuf 2>&1 | tail -5

Defaulting to user installation because normal site-packages is not writeable
ERROR: Could not find a version that satisfies the requirement ffuf (from versions: none)
ERROR: No matching distribution found for ffuf
$ python3 -c "
import urllib.request, sys
url = 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=30).read().decode()
    with open('/tmp/common.txt','w') as f:
        f.write(data)
    print(f'Downloaded {len(data.splitlines())} lines')
except Exception as e:
    print(f'Error: {e}')
" 2>&1

Downloaded 4751 lines
$ python3 -c "
import urllib.request, sys
url = 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-medium-words-lowercase.txt'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=30).read().decode()
    with open('/tmp/raft-medium.txt','w') as f:
        f.write(data)
    print(f'Downloaded {len(data.splitlines())} lines')
except Exception as e:
    print(f'Error: {e}')
" 2>&1

Downloaded 56293 lines
$ python3 -c "
import urllib.request, sys
url = 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/ASP.txt'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=30).read().decode()
    with open('/tmp/asp.txt','w') as f:
        f.write(data)
    print(f'Downloaded {len(data.splitlines())} lines')
except Exception as e:
    print(f'Error: {e}')
" 2>&1

Error: HTTP Error 404: Not Found
$ python3 -c "
import urllib.request
urls = {
    '/tmp/asp_txt.txt': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt',
}
for path, url in urls.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=30).read().decode()
        with open(path,'w') as f: f.write(data)
        print(f'{path}: {len(data.splitlines())} lines')
    except Exception as e:
        print(f'{url}: {e}')
" 2>&1

/tmp/asp_txt.txt: 6453 lines
$ python3 << 'PYEOF'
import urllib.request, json, sys, socket, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# CRT.sh for subdomains
try:
    req = urllib.request.Request("https://crt.sh/?q=%.structuredweb.dell.com&output=json", headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=20, context=ctx).read().decode()
    subs = set()
    for entry in json.loads(data):
        name = entry.get('name_value','')
        for n in name.split('\n'):
            n = n.strip()
            if n.endswith('structuredweb.dell.com'):
                subs.add(n)
    for s in sorted(subs):
        print(s)
except Exception as e:
    print(f"CRT error: {e}", file=sys.stderr)

# Also check structuredweb.com subdomains
try:
    req = urllib.request.Request("https://crt.sh/?q=%.structuredweb.com&output=json", headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=20, context=ctx).read().decode()
    subs = set()
    for entry in json.loads(data):
        name = entry.get('name_value','')
        for n in name.split('\n'):
            n = n.strip()
            if n.endswith('structuredweb.com'):
                subs.add(n)
    for s in sorted(subs):
        print(s)
except Exception as e:
    print(f"CRT structuredweb error: {e}", file=sys.stderr)
PYEOF

CRT structuredweb error: HTTP Error 404: Not Found
structuredweb.dell.com
$ python3 << 'PYEOF'
import urllib.request, sys, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

paths = [
    "/sw/admin/", "/admin/", "/swchannel/", "/sw/login.asp", "/sw/admin.asp",
    "/swchannel/admin/", "/swchannel/login.asp", "/swchannel/default.asp",
    "/sw/default.asp", "/default.asp", "/index.asp", "/login.asp",
    "/sw/swchannel/", "/api/", "/sw/api/", "/swchannel/api/",
    "/.env", "/robots.txt", "/sitemap.xml", "/sw/web.config",
    "/web.config", "/swchannel/submit_signup.asp", "/sw/scripts/",
    "/sw/themes/", "/sw/app/", "/Scripts/", "/swchannel/process.asp",
    "/swchannel/register.asp", "/backup/", "/sw/backup/",
    "/swchannel/backup/", "/sw/include/", "/swchannel/include/",
    "/sw/_private/", "/swchannel/_private/",
    "/cfide/", "/sw/cfide/",
]

base = "https://structuredweb.dell.com"
for p in paths:
    try:
        url = base + p
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        code = resp.getcode()
        size = len(resp.read())
        if code != 404 and code != 403:
            print(f"[{code}] ({size}B) {p}")
        resp.close()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[{e.code}] {p}")
    except Exception as e:
        pass
PYEOF

[200] (9596B) /sw/admin/
[200] (3239B) /admin/
[200] (3239B) /swchannel/
[200] (9596B) /sw/login.asp
[200] (3239B) /sw/admin.asp
[200] (3239B) /swchannel/admin/
[200] (3239B) /swchannel/login.asp
[200] (3239B) /swchannel/default.asp
[200] (9596B) /sw/default.asp
[200] (3239B) /default.asp
[200] (3239B) /index.asp
[200] (3239B) /login.asp
[403] /sw/swchannel/
[200] (3239B) /api/
[200] (3239B) /sw/api/
[200] (3239B) /swchannel/api/
[403] /.env
[200] (300B) /robots.txt
[200] (3239B) /sw/web.config
[200] (3239B) /web.config
[200] (3239B) /swchannel/submit_signup.asp
[403] /sw/scripts/
[403] /sw/themes/
[200] (9596B) /sw/app/
[403] /Scripts/
[200] (3239B) /swchannel/process.asp
[200] (3239B) /swchannel/register.asp
[200] (3239B) /backup/
[200] (3239B) /sw/backup/
[200] (3239B) /swchannel/backup/
[200] (3239B) /sw/include/
[200] (3239B) /swchannel/include/
[200] (3239B) /sw/_private/
[200] (3239B) /swchannel/_private/
[396] /cfide/
[396] /sw/cfide/
$ curl -sI "https://structuredweb.dell.com/sw/admin/" 2>&1 | head -20

HTTP/2 302 
date: Tue, 09 Jun 2026 09:26:45 GMT
content-type: text/html
content-length: 145
cache-control: private,no-store
pragma: no-cache
location: /sw/site/login/login.asp
server: StructuredWeb
set-cookie: ASPSESSIONIDSAQTRTQQ=PGNLFBJDPFNCNDHMPNALNPDO; path=/
content-security-policy: default-src https: http: data: wss: blob: 'unsafe-inline'; object-src 'none'; script-src 'self' https: http: 'unsafe-eval' 'unsafe-inline'
referrer-policy: strict-origin-when-cross-origin
strict-transport-security: max-age=15768000; includeSubDomains
x-content-type-options: nosniff

$ curl -sI "https://structuredweb.dell.com/sw/login.asp" 2>&1 | head -20

HTTP/2 302 
date: Tue, 09 Jun 2026 09:26:46 GMT
content-type: text/html
content-length: 145
cache-control: private,no-store
pragma: no-cache
location: /sw/site/login/login.asp
server: StructuredWeb
set-cookie: ASPSESSIONIDAQBSBDTC=DAHHIJNDGACJIJKPNBFFGMBN; path=/
content-security-policy: default-src https: http: data: wss: blob: 'unsafe-inline'; object-src 'none'; script-src 'self' https: http: 'unsafe-eval' 'unsafe-inline'
referrer-policy: strict-origin-when-cross-origin
strict-transport-security: max-age=15768000; includeSubDomains
x-content-type-options: nosniff

$ curl -sI "https://structuredweb.dell.com/.env" 2>&1 | head -20

HTTP/2 403 
server: awselb/2.0
date: Tue, 09 Jun 2026 09:26:46 GMT
content-type: text/html
content-length: 118

$ curl -s "https://structuredweb.dell.com/robots.txt" 2>/dev/null

User-agent: *
Disallow: /sw/swchannel/productcatalogcf_v2/internet
Disallow: /sw/swchannel/productcatalogcf_v2/internet/
Disallow: /sw/swchannel/productcatalogcf_v2/internet/*
Disallow: /sw/swchannel/productcatalogcf_v2/internet/*.asp
Disallow: /sw/swchannel/productcatalogcf_v2/internet/*.cfm
$ curl -s "https://structuredweb.dell.com/sw/swchannel/" 2>&1 | head -50

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
<title>403 - Forbidden: Access is denied.</title>
<style type="text/css">
<!--
body{margin:0;font-size:.7em;font-family:Verdana, Arial, Helvetica, sans-serif;background:#EEEEEE;}
fieldset{padding:0 15px 10px 15px;} 
h1{font-size:2.4em;margin:0;color:#FFF;}
h2{font-size:1.7em;margin:0;color:#CC0000;} 
h3{font-size:1.2em;margin:10px 0 0 0;color:#000000;} 
#header{width:96%;margin:0 0 0 0;padding:6px 2% 6px 2%;font-family:"trebuchet MS", Verdana, sans-serif;color:#FFF;
background-color:#555555;}
#content{margin:0 0 0 2%;position:relative;}
.content-container{background:#FFF;width:96%;margin-top:8px;padding:10px;position:relative;}
-->
</style>
</head>
<body>
<div id="header"><h1>Server Error</h1></div>
<div id="content">
 <div class="content-container"><fieldset>
  <h2>403 - Forbidden: Access is denied.</h2>
  <h3>You do not have permission to view this directory or page using the credentials that you supplied.</h3>
 </fieldset></div>
</div>
</body>
</html>
$ curl -sI "https://structuredweb.dell.com/sw/site/login/login.asp" 2>&1 | head -20

HTTP/2 200 
date: Tue, 09 Jun 2026 09:26:53 GMT
content-type: text/html
content-length: 9596
cache-control: no-cache,no-store
pragma: no-cache
server: StructuredWeb
p3p: CP="NON NOR OUR CONo"
set-cookie: loginType=7MqrB8NQ5LrAaGYDhpRljA2; expires=Tue, 09-Jun-2026 10:26:52 GMT; path=/
set-cookie: SWCONTEXTLONG=0; path=/
set-cookie: SWSESSIONID=E292686EF8A48195101B1598C981FA77; path=/
set-cookie: ASPSESSIONIDSAQTRTQQ=AHNLFBJDLIHAOBEHDPAIHHPC; path=/
content-security-policy: default-src https: http: data: wss: blob: 'unsafe-inline'; object-src 'none'; script-src 'self' https: http: 'unsafe-eval' 'unsafe-inline'
referrer-policy: strict-origin-when-cross-origin
strict-transport-security: max-age=15768000; includeSubDomains
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN

$ curl -s "https://structuredweb.dell.com/sw/site/login/login.asp" 2>/dev/null | head -100

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html;charset=utf-8">
<!-- Copyright (c) StructuredWeb 1999-2007 -->
<!-- SERVER=swmail01 -->
<link REL='stylesheet' HREF='/sw/themes/5/theme5.css' TYPE='text/css'><title>StructuredWeb</title>



<link href="/sw/app/CommonUI/CSS/global.css" rel="stylesheet" type="text/css" />
<link href="/sw/app/CommonUI/CSS/fonts/ss-pika/webfonts/ss-pika.css" type="text/css" rel="stylesheet">


<script language="JavaScript" SRC="/sw/scripts/sw_funcs.js"></script>
<script language="JavaScript">

    if (location.href.includes("newlogin=1")) {
        location.href = "/sw/app/Login/v2/loginRedirect.aspx?vendor=shareRedirect&scope=" + location.href.split("SWSCOPEID=")[1].split("&")[0] + "&csid=" + location.href.split("DefaultLibraryID=")[1].split("&")[0];
    }

    function showHideAccountHelp() {
        var helpTextElem = document.getElementById("accountHelp");

        if (helpTextElem.style.display == 'none') {
            helpTextElem.style.display = 'block';
        }
        else {
            helpTextElem.style.display = 'none';
        }
    }

    // Functions From sw_funcs.js
    function load_swLogin() {
        top.document.swLogin.txtUserName.focus();
    }
    function load_swAddrLogin() {
        top.document.swLogin.txtSiteAddress.focus();
    }
    function chk_swUser() {
        //alert("sw_User");

        var isOk
        var FieldUserName = document.swLogin.txtUserName
        var FieldPassword = document.swLogin.txtPassword

        if (typeof (document.swLogin.LoginUserID) != 'undefined') {
            var FieldLoginCookie = document.swLogin.LoginUserID;
            if (!IsEmpty(FieldLoginCookie)) {
                var ab = document.getElementById("btnSubmit");
                ab.disabled = true;
                document.swLogin.submit();
            }
        }

        isOk = IsEmpty(FieldUserName)
        if (isOk) {
            isOk = IsEmpty(FieldPassword)
        }
        if (isOk) {
            var ab = document.getElementById("btnSubmit");
            ab.disabled = true;
            document.swLogin.submit();
        }

    }
    function chk_swUserURL() {
        //alert("sw_UserURL");

        var isOk
        var FieldSiteAddress = document.swLogin.txtSiteAddress
        var FieldUserName = document.swLogin.txtUserName
        var FieldPassword = document.swLogin.txtPassword
        var Patern = document.swLogin.patern.value

        if (typeof (document.swLogin.LoginUserID) != 'undefined') {
            var FieldLoginCookie = document.swLogin.LoginUserID;
            if (!IsEmpty(FieldLoginCookie)) {
                var ab = document.getElementById("btnSubmit");
                ab.disabled = true;
                document.swLogin.submit();
            }
        }

        isOk = IsEmpty(FieldSiteAddress)
        var iSiteAddress = parseInt(FieldSiteAddress.value);
        if (parseInt(FieldSiteAddress.value) > 2147483647) {
            alert("Invalid Account ID. Please enter a valid Account ID.");
            isOk = false;
        }

        if (isOk) {
            isOk = IsEmpty(FieldUserName)
            if (isOk) {
                isOk = IsEmpty(FieldPassword)
            }
            if (isOk) {
                var PaternSiteAddress = document.swLogin.txtSiteAddress.value.toLowerCase()
                var re = new RegExp(Patern)
                var FormatSiteAddress = document.swLogin.WebSiteAddress.value
$ python3 << 'PYEOF'
import urllib.request, sys, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = "https://structuredweb.dell.com"
paths = [
    "/sw/swchannel/productcatalogcf_v2/internet/",
    "/sw/swchannel/productcatalogcf_v2/",
    "/sw/swchannel/productcatalogcf_v2/internet/index.cfm",
    "/sw/swchannel/productcatalogcf_v2/internet/admin.cfm",
    "/CFIDE/administrator/",
    "/CFIDE/administrator/index.cfm",
    "/CFIDE/administrator/enter.cfm",
    "/sw/CFIDE/administrator/",
    "/sw/cfide/administrator/",
    "/sw/site/",
    "/sw/site/login/",
    "/sw/site/admin/",
    "/swchannel/productcatalogcf_v2/",
]

for p in paths:
    try:
        url = base + p
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        code = resp.getcode()
        size = len(resp.read())
        if code != 404:
            print(f"[{code}] ({size}B) {p}")
        resp.close()
    except urllib.error.HTTPError as e:
        if e.code not in [404]:
            print(f"[{e.code}] {p}")
    except Exception as e:
        print(f"[ERR] {p}: {e}")
PYEOF

[403] /sw/swchannel/productcatalogcf_v2/internet/
[403] /sw/swchannel/productcatalogcf_v2/
[200] (3239B) /sw/swchannel/productcatalogcf_v2/internet/index.cfm
[200] (3239B) /sw/swchannel/productcatalogcf_v2/internet/admin.cfm
[396] /CFIDE/administrator/
[396] /CFIDE/administrator/index.cfm
[396] /CFIDE/administrator/enter.cfm
[396] /sw/CFIDE/administrator/
[396] /sw/cfide/administrator/
[403] /sw/site/
[403] /sw/site/login/
[200] (3239B) /sw/site/admin/
[200] (3239B) /swchannel/productcatalogcf_v2/
$ curl -s "https://structuredweb.dell.com/sw/site/login/login.asp" 2>/dev/null | tail -200

            alert("Invalid Account ID. Please enter a valid Account ID.");
            isOk = false;
        }

        if (isOk) {
            isOk = IsEmpty(FieldUserName)
            if (isOk) {
                isOk = IsEmpty(FieldPassword)
            }
            if (isOk) {
                var PaternSiteAddress = document.swLogin.txtSiteAddress.value.toLowerCase()
                var re = new RegExp(Patern)
                var FormatSiteAddress = document.swLogin.WebSiteAddress.value
                if (PaternSiteAddress.search(re) == -1) {
                    //alert("Url not valid")
                    //alert ("Your website address must have the format:  " + FormatSiteAddress + "\nThat is, your fully qualified domain name, starting with 'www'")
                    //document.swLogin.txtSiteAddress.focus();
                    //document.swLogin.txtSiteAddress.select();
                    //isOk = false;
                }

            }
        }
        if (isOk) {
            var ab = document.getElementById("btnSubmit");
            ab.disabled = true;
            document.swLogin.submit();
        }
    }

    function FlipRememberCheck() {
        var CheckAddress = document.swLogin.chkRemember;
        if (CheckAddress.checked) {
            CheckAddress.checked = false;
        }
        else {
            CheckAddress.checked = true;
        }
    }

</script>

</script>



</head>

<script language="JavaScript"> 
    function DaughterWindow(URL) {
        open(URL, "", "resizable,width=800,height=600,scrollbars=yes");
    }

    function DaughterWindowHelp(URL) {
        xWindow = window.open(URL, "", "resizable,width=700,height=500,top=0,left=0,scrollbars=yes");
    }
</script>

<body >


<!--[if lte IE 9]>
<div class="centeredwrapper_quirky">
<div class="centeredwrapper_quirky_fix">
<![endif]-->
<!--[if (gt IE 9)|!(IE)]><!--> 
<div class="centeredwrapper">
<!--<![endif]-->

	<div class="login_logo">
	
		<!--[if lte IE 9]>
		<div class="login_logo_quirky">
		<![endif]-->
	
		<div class="login_logo_figure">
			<img SRC="/sw/themes/5/images/logo_login_32.gif" ALT="StructuredWeb">
		</div>
		
		<h1>Login</h1>
		
		<!--[if lte IE 9]>
		</div>
		<!--<![endif]-->
	
	</div>
	
	<!---
	<a href="Javascript:DaughterWindow('/sw/swchannel/UserManual/UserManual.cfm?AppID=24&amp;MethodID=-1');">
			<img SRC="/sw/themes/5/images/help2.gif" border="0" ALT="StructuredWeb HelpCenter" hspace="5" vspace="5">
		</a>
	-->	

	<div class="login_formbg">
	
	<form method="POST" action="/sw/app/Login/v2/loginRedirect.aspx" name="swLogin" onsubmit="chk_swUserURL();return false;">
	
		
	<div id="loginBoxDiv">
		
		
		<label class="login_box_text">
			Account ID<a class="project" href="javascript:showHideAccountHelp();"><img src="/sw/app/CommonUI/Images/Button/blue_question_sm.gif" width="14" height="15" alt=""></a>
		</label>
	
	
	<div id="accountHelp" style="display: none;" class="login_checkboxtext">
		<span>Please enter your Account ID (ex. 1792)</span>
	</div>
	
			<input name="txtSiteAddress" type="text" maxlength="120" class="login_formfield login_padbuttom1" value="" tabindex="1">
			
			<label class="login_box_text">Username</label>

			

			<input type="text" name="txtUserName" maxlength="50" class="login_formfield login_padbuttom2" value="" tabindex="2">

				
				<label class="login_box_text login_forget">Password <a href="/sw/app/Login/PWHelp.aspx">I forgot</a></label>
			
					<input type="password" name="txtPassword" class="login_formfield" maxlength="50" value="" tabindex="3" autocomplete="off">
				
			<input type="hidden" name="isHashedPassword" value="False">
			


				<input type="hidden" name="iAttempts" value="0">
				<input type="hidden" name="WebSiteAddress" value="www.empiretech.atworkweb.com">
				<input type="hidden" id="patern" name="patern" value="^((([www]+(\.[a-z0-9-]+)*(\.[a-z]{2,4}))|(([0-9]{1,4}\.){3}([0-9]{1,3})))((/|\?)[a-z0-9~#%&amp;'_\+=:\?\.-]*)*)$">
				<input type="hidden" name="testForJs" id="testForJs" value="">
			
			
			
			<div class="login_pading"  style='display: none'>
				<input type="checkbox" id="chkRemember" class="login_checkbox"  name="chkRemember" value="1">
				<label class="login_checkboxtext" onclick="FlipRememberCheck();">Keep me signed in for 24 hours<span>Don't check this box if you're at a public or shared computer</span>
				</label>
			</div>

			
			<input type="image" tabindex="4" class="login_buttonpad" src="/sw/app/CommonUI/Images/Button/login_button.gif" value="Continue" id="btnSubmit" name="btnSubmit" onclick="chk_swUserURL();return false;">
			
				
		<input type="hidden" name="scope" value="intranet">
	</div>
	</form>		
	
	
	
	<!--[if lte IE 9]>
		</div>
	<!--<![endif]-->
		
	</div>
	
	<script language="javascript">
        document.getElementById('testForJs').value = "hasJs";
	

	

            load_swAddrLogin();
    </script>


</div>
<!-- Google Code for Login page retargeting tag [Managed by template audience id 0] Conversion Page -->
<!-- Remarketing tags may not be associated with personally identifiable information or placed on pages related to sensitive categories. For instructions on adding this tag and more information on the above requirements, read the setup guide: google.com/ads/remarketingsetup -->
<script type="text/javascript">

    // append to loginredirect
    setTimeout(() => {
        if (location.href.split("?")[1].toLowerCase().includes("isshareurl")) {
            document.swLogin.action = document.swLogin.action + "?vendor=shareLink"
        }

        else {
            document.swLogin.action = document.swLogin.action + "?vendor=classicLogin"
        }
    }, 0);


    /* <![CDATA[ */
    var google_conversion_id = 1072668527;
    var google_conversion_label = "su2rCKuzoV8Q776-_wM";
    var google_custom_params = window.google_tag_params;
    var google_remarketing_only = true;
    /* ]]> */
</script>
<script type="text/javascript" src="//www.googleadservices.com/pagead/conversion.js">
</script>
<noscript>
<div style="display:inline;">
<img height="1" width="1" style="border-style:none;" alt="" src="//googleads.g.doubleclick.net/pagead/viewthroughconversion/1072668527/?value=1.00&amp;currency_code=USD&amp;label=su2rCKuzoV8Q776-_wM&amp;guid=ON&amp;script=0"/>
</div>
</noscript>
</body>

</html>
$ curl -sI "https://structuredweb.dell.com/sw/app/Login/v2/loginRedirect.aspx" 2>&1 | head -20

HTTP/2 200 
date: Tue, 09 Jun 2026 09:27:13 GMT
content-type: text/html; charset=utf-8
content-length: 472
cache-control: private,no-store
pragma: no-cache
server: StructuredWeb
p3p: CP="NON NOR OUR CONo"
content-security-policy: default-src https: http: data: wss: blob: 'unsafe-inline'; object-src 'none'; script-src 'self' https: http: 'unsafe-eval' 'unsafe-inline'
referrer-policy: strict-origin-when-cross-origin
strict-transport-security: max-age=15768000; includeSubDomains
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN

$ curl -sI "https://structuredweb.dell.com/CFIDE/administrator/" 2>&1 | head -20

HTTP/2 396 
server: awselb/2.0
date: Tue, 09 Jun 2026 09:27:14 GMT
content-length: 42
content-type: text/plain

$ curl -s "https://structuredweb.dell.com/CFIDE/administrator/" 2>/dev/null | head -50

403 Forbidden
Reference Code: AB12CD34EF08
#!/usr/bin/env python3
import urllib.request, sys, ssl, threading, time, queue, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = sys.argv[1]
WORDLIST = sys.argv[2]
THREADS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
EXT = sys.argv[4] if len(sys.argv) > 4 else ""

results = []
lock = threading.Lock()
q = queue.Queue()

def worker():
    while True:
        try:
            word = q.get(timeout=1)
        except:
            break
        word = word.strip()
        if not word or word.startswith('#'):
            q.task_done()
            continue
        try:
            path = f"{BASE}/{word}{EXT}"
            req = urllib.request.Request(path, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
            resp = urllib.request.urlopen(req, timeout=8, context=ctx)
            code = resp.getcode()
            size = len(resp.read())
            resp.close()
            if code not in [404] and size != 3239:
                with lock:
                    results.append(f"[{code}] ({size}B) /{word}{EXT}")
                    sys.stdout.write(f"[{code}] ({size}B) /{word}{EXT}\n")
                    sys.stdout.flush()
        except urllib.error.HTTPError as e:
            if e.code not in [404, 410]:
                with lock:
                    results.append(f"[{e.code}] /{word}{EXT}")
                    sys.stdout.write(f"[{e.code}] /{word}{EXT}\n")
                    sys.stdout.flush()
        except Exception as e:
            pass
        q.task_done()

with open(WORDLIST) as f:
    for line in f:
        q.put(line.strip())

print(f"[*] Fuzzing {BASE} with {q.qsize()} words, {THREADS} threads, ext={EXT}")
for _ in range(THREADS):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
q.join()
print(f"\n[*] Done. Found {len(results)} results.")
for r in results:
    print(r)
$ curl -s "https://structuredweb.dell.com/sw/app/Login/v2/loginRedirect.aspx" 2>/dev/null | head -100

<form id='submitForm' method='POST' action='/sw/site/login/submit_login.asp?newlogin=False&vendor=structuredweb' hidden></form><script>localStorage.clear(); setTimeout(() => {document.getElementById('submitForm').submit();}, 0)</script><form id='submitForm' method='POST' action='/sw/site/login/submit_login.asp?newlogin=False&vendor=structuredweb' hidden></form><script>localStorage.clear(); setTimeout(() => {document.getElementById('submitForm').submit();}, 0)</script>
$ curl -s "https://structuredweb.dell.com/sw/app/Login/PWHelp.aspx" 2>/dev/null | head -100


<!DOCTYPE html>
<meta http-equiv="X-UA-Compatible" content="IE=edge" />  
<html xmlns="http://www.w3.org/1999/xhtml" >
	
    <!-- Version: 2026-6-1_212117 -->
    <!-- Branch: main -->
    <head>
        
<script type="text/javascript" src="//use.typekit.net/nsv4xcc.js"></script>
<script src="https://structuredweb.dell.com/sw/app/CommonUI/JS/Vendor/loadTypekit.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>
<link rel="stylesheet" href="https://filestorage.structuredweb.com/common/ss-pika/webfonts/ss-pika.css">
<!-- setup js/css and things that are always included-->
<script src="https://structuredweb.dell.com/sw/app/CommonUI/JS/global.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>
<script src="https://structuredweb.dell.com/sw/app/CommonUI/JS/formHelper.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>
<script src="https://filestorage.structuredweb.com/common/ss-pika/webfonts/ss-pika.js" language="javascript" type="text/javascript"></script>

<script src="https://structuredweb.dell.com/sw/app/CommonUI/js/jquery.min.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>  
<script src="https://structuredweb.dell.com/sw/app/CommonUI/js/jquery-migrate.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>  
    <script src="https://structuredweb.dell.com/sw/app/CommonUI/js/lib/bootstrap.min.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>
<link rel="StyleSheet" href="https://structuredweb.dell.com/sw/app/CommonUI/CSS/themeLegacy.css?v=2026-6-1_212117" type="text/css" />
<link rel="StyleSheet" href="https://structuredweb.dell.com/sw/app/CommonUI/CSS/bootstrap/bootstrap.min.css?v=2026-6-1_212117" type="text/css" />
<link rel="StyleSheet" href="https://structuredweb.dell.com/sw/app/CommonUI/CSS/global.css?v=2026-6-1_212117" type="text/css"/>
<link rel="StyleSheet" href="https://structuredweb.dell.com/sw/app/CommonUI/CSS/ui.css?v=2026-6-1_212117" type="text/css"/>

        <script src="https://structuredweb.dell.com/sw/app/CommonUI/JS/resizeIFrame.js?v=2026-6-1_212117" language="javascript" type="text/javascript"></script>
        
    <title>Password Reset</title>
    
    
    <script src='https://www.google.com/recaptcha/api.js'></script>

        <script language="javascript" type="text/javascript">
            function OnLoad() 
            {
                
			    
            }
        </script>
        
    </head>
    
    
    <body class="aspBody " onload="OnLoad()">
		<div class="aspContainer container">	
            
<div class="centeredwrapper">
    <div class="login_logo">
		<div class="login_logo_figure">
		</div>
	</div>
    <div>
        <span style="display: none;" id="spanErrorText"></span>
    </div>
    <div class="login_formbg3">
        <div class="login_checkboxtext2">
            <span id="spanText">
                Please enter your account ID and either your username or email address and click send. An email with a password reset link will be sent to your email address.
		        <br/><br/>
                If you don&#39;t know your account ID, username or email, please contact your site administrator.
                
	        </span>
            <br/>
        </div>
        <br />
        <div class="split"></div><br />
     
                <div class="requestText ">
                    <span> Reset Your Password Using:</span>
                </div><br />
         
        <div class="container">
            <div class="col-md-2"></div>
            <div class="col-md-4">
                <button class="btn btn-block btn-secondary custom-btn2" onclick="event.PreventDefault; event.StopPropagation; showEmailForm();">
                    Email
                </button>
            </div>
            <div class="col-md-4">
                <button class="btn btn-block btn-secondary custom-btn2" onclick="event.PreventDefault; event.StopPropagation; showIdUnForm()">
                    Username
                </button>
            </div>
            <div class="col-md-2"></div>        
        </div>
        <br /><br /><br />
        <div class="split"></div><br /> 
        <form name="frm1" method="post" action="get">
            
            
            <div class="login_checkboxtext2larger">
                <span>
	                Account ID
	            </span>
            </div>
		    <input 
			    type="text"
			    name="txtWebAddress" 
                id="txtWebAddress" 
			    value="" 
$ curl -sI "https://structuredweb.dell.com/sw/swchannel/UserManual/UserManual.cfm?AppID=24&MethodID=-1" 2>&1 | head -20

HTTP/2 302 
date: Tue, 09 Jun 2026 09:27:28 GMT
content-type: text/html;charset=UTF-8
content-length: 0
location: https://structuredweb.dell.com/sw/app/Login/v2/loginRedirect.aspx?vendor=structuredweb
cache-control: no-cache,no-store
pragma: no-cache,no-cache
server: StructuredWeb
content-security-policy: default-src https: http: data: wss: blob: 'unsafe-inline'; object-src 'none'; script-src 'self' https: http: 'unsafe-eval' 'unsafe-inline'
referrer-policy: strict-origin-when-cross-origin
strict-transport-security: max-age=15768000; includeSubDomains
x-content-type-options: nosniff

$ curl -s "https://structuredweb.dell.com/sw/app/CommonUI/JS/global.js" 2>/dev/null | head -400

function getGenericShareLink(callback) {
    var URL = location.href.replace(/SWSESSIONID=\w*&?/, "");
    $.ajax({
        url: "/sw/app/ServicePages/Campaign/GetShareURLGeneric.aspx",
        type: 'post',
        data: { "URL": URL },
        success: (res) => {
            callback(res);
        },
        error: () => {
            callback("Could Not Get Share Link");
        }
    });
}

function getInternetExplorerVersion()
// Returns the version of Internet Explorer or a -1
// (indicating the use of another browser).
{
    var rv = 999; // Return value assumes failure or not IE
    if (navigator.appName == 'Microsoft Internet Explorer') {
        var ua = navigator.userAgent;
        var re = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
        if (re.exec(ua) != null)
            rv = parseFloat(RegExp.$1);
    }
    return rv;
}

function parseJSON(jsonData) {
    var browserVersion = getInternetExplorerVersion();

    if (browserVersion < 999) {
        jsonData = eval('(' + jsonData + ')');
    }
    else {
        jsonData = JSON.parse(jsonData);
    }
    return jsonData;
}

//also in sw_funcs
function addUrlParameters(url, parameters) {
    if (parameters.length % 2 == 0) {
        var seperator = '?';
        if (url.indexOf('?') != -1) {
            seperator = '&';
        }

        for (var i = 0; i < parameters.length; i = i + 2) {
            url += seperator + parameters[i] + '=' + parameters[i + 1];
            seperator = '&';
        }
    }
    return url;
}

function buildAjaxData(parameters) {
    var seperator = '&';
    var result = '';
    if (parameters.length % 2 == 0) {
        for (var i = 0; i < parameters.length; i = i + 2) {
            result += (i == 0 ? '' : seperator);
            result += parameters[i] + '=' + parameters[i + 1];
        }
    }
    return result;
}

function encodeParams(params) {
    var encodedParams = [];
    for (var i = 0; i < params.length; i++) {
        encodedParams[i] = encodeURIComponent(params[i]);
    }
    return encodedParams;
}

function simpleAjax(urlId, callback, errorCallback, data) {
    var url = document.getElementById(urlId).value;
    var params = new Array();
    params.push("ajax");
    params.push("true");
    var opts = { params: params, disableCache: true };

    if (data) {
        ajaxPost(url, callback, errorCallback, data, opts);
    } else {
        ajaxGet(url, callback, errorCallback, opts);
    }
}

function simpleHTMLInjectionAjax(urlId, injectTargetId, errorCallback, data) {
    var callback = function (result) { document.getElementById(injectTargetId).innerHTML = result; };
    simpleAjax(urlId, callback, errorCallback, data);
}

function simpleJsonAjax(urlId, callback, errorCallback, data) {
    var foo = function (result) { AjaxJsonResponseCallback(result, callback); };
    simpleAjax(urlId, foo, errorCallback, data);
}

function ajaxGet(url, callback, errorCallBack, opts) {
    if (typeof opts === "undefined") {
        opts = { method: 'GET' };
    }
    else if (typeof opts.method === "undefined") {
        opts.method = 'GET';
    }
    SWAjax(url, callback, errorCallBack, null, opts);
}

function ajaxPost(url, callback, errorCallBack, data, opts) {
    if (typeof opts === "undefined") {
        opts = { method: 'POST' };
    }
    else if (typeof opts.method === "undefined") {
        opts.method = 'POST';
    }

    data = AttachCSRFToken(data, "CSRFToken");
    SWAjax(url, callback, errorCallBack, data, opts);
}

function isLoginURL(url) {
    if (url && typeof url == "string") {
        return (url.indexOf('site/login/login.asp') >= 0);
    }
    return false;
}

// <summary>
// available parameters in opts
// params : additional url params that are going to be urlencoded
// disableCache : in order to disable cache, it passes additional url param with timestamp
// example
//var url = location.href;
// var params = new Array();
// params.push("ajax");
// params.push("true");
// params.push("isOptionNameDupliacte");
// params.push("True");
// params.push("optionName");
// params.push(optionName);
// ajaxGet(url, callbackCheckDuplicationOption, globalAjaxErrorHandler, { params: params, disableCache: true });
// </summary>
function SWAjax(url, callback, errorCallBack, data, opts) {
    var disableCachingParam = 'rnd';

    if (typeof errorCallBack === "undefined") {
        errorCallBack = globalAjaxErrorHandler;
    }

    if (typeof opts !== "undefined" && typeof opts.params !== "undefined") {
        var params = encodeParams(opts.params);
        url = addUrlParameters(url, params);
    }

    if (typeof opts !== "undefined" && typeof opts.disableCache !== "undefined") {
        url = addUrlParameters(url, [disableCachingParam, new Date().getTime()]);
    }

    var method = "GET";
    if (typeof opts !== "undefined" && typeof opts.method !== "undefined") {
        method = opts.method;
    }

    var xmlhttp;
    if (window.XMLHttpRequest) {
        // code for IE7+, Firefox, Chrome, Opera, Safari
        try {
            xmlhttp = new XMLHttpRequest();
        }
        catch (whatThe) {
            xmlhttp = new window.XMLHttpRequest();
        }
    } else {
        // code for IE6, IE5
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            if (xmlhttp.responseURL && isLoginURL(xmlhttp.responseURL)) {
                window.location = xmlhttp.responseURL;
            } else {
                callback(xmlhttp.responseText);
            }

        }
        else if (xmlhttp.readyState == 4 && (xmlhttp.status == 500 || xmlhttp.status == 400 || xmlhttp.status == 403)) {
            //return JSON Object
            try {
                var result = xmlhttp.responseText;
                result = parseJSON(result);
                errorCallBack(result);
            } catch (e) {
                errorCallBack(xmlhttp.responseText);
            }
        }
    };

    xmlhttp.open(method, url, true);

    if (method == 'POST') {
        xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    }

    xmlhttp.send(data);
}

function globalAjaxErrorHandler(message) {
    //do nothing
}

//ajax callback wrapper, assumes the response is JSON if it is not or if the object is a SWAjaxError (has errorInfo and display properties)
//treats it as an error and displays an apropriate error message, return true on success and calls onSuccess (see also: AjaxResponseCallback)
//onSWError is only called if an SWAjaxError is returned with display false
function AjaxJsonResponseCallback(result, onSuccess, onSWError) {
    var resultObj;
    try {
        resultObj = JSON.parse(result);
        if (typeof resultObj.errorInfo !== "undefined" && typeof resultObj.display !== "undefined") {
            if (resultObj.display == true) {
                alert(resultObj.errorInfo);
                return false;
            } else {
                onSWError(resultObj);
                return false;
            }
        }
    }
    catch (ex) {
        var defaultErrorMessage = getValue('Ajax_Update_Error_Message');
        alert(defaultErrorMessage);
        return false;
    }
    if (onSuccess) {
        onSuccess(resultObj);
    }
    return true;
}

//ajax callback wrapper assumes the response is not JSON but tries to parse the response as JSON incase it is a JSON representation of SWAjaxError
//in the case of SWAjaxError handles it as apropriate and returns false, else returns true and calls onSuccess (see also: AjaxJsonResponseCallback)
//onSWError is only called if an SWAjaxError is returned with display false
function AjaxResponseCallback(result, onSuccess, onSWError) {
    try {
        var resultObj = JSON.parse(result);
        if (typeof resultObj.errorInfo !== "undefined" && typeof resultObj.display !== "undefined") {
            if (resultObj.display == true) {
                alert(resultObj.errorInfo);
                return false;
            } else {
                onSWError(resultObj);
                return false;
            }
        }
    }
    catch (ex) { }

    if (onSuccess) {
        onSuccess(result);
    }
    return true;
}

function createCookie(name, value, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function createCookieWithPath(name, value, days, path) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=" + path;
}

function eraseCookie(name) {
    createCookie(name, "", -1);//clear out the values and make it expire
}

function navigate(url) {
    window.location = url;
}
//popup/display related stuff
function showElement(ele) {
    if (ele) {
        ele.style.display = "block";
    }
}
function showElementInline(ele) {
    if (ele) {
        ele.style.display = "inline";
    }
}

function showElementInlineBlock(ele) {
    if (ele) {
        ele.style.display = "inline-block";
    }
}

function hideElement(ele) {
    if (ele) {
        ele.style.display = "none";
    }
}

function hideElements(eles) {
    for (var i = 0; i < eles.length; i++) {
        hideElement(eles[i]);
    }
}

//For when display none doesn't cut it
//ex: http://stackoverflow.com/questions/2345784/jquery-get-height-of-hidden-element-in-jquery
function showElementVisibility(ele) {
    ele.style.visibility = "visible";
}
function hideElementVisibility(ele) {
    ele.style.visibility = "hidden";
}

/* call to ss-pika JS function to show ss-pika icons, usually this needs to be done in old versions of IE for when data is fetched via JS that may have the ss-pika icons */
function reloadIcons() {
    //if we have an older browser which doesn't have the getElementsByClassName feature (i.e. IE8)
    if (typeof ss_legacy !== 'undefined') {
        if (!document.getElementsByClassName) {
            ss_legacy(ss_getElementsByClassName(document.body, 'ss-icon'));
        } else {
            ss_legacy(document.getElementsByClassName('ss-icon'));
        }
    }
}

function showPopup(idName) {

    //it appends a backdrop div to the body, sets a class on the body for overflow prevention
    //and actually displays the popup
    var $element = $('#' + idName);
    if ($element.modal) {
        if ($('.modal-backdrop').length != 0) {
            $('.modal-backdrop').remove();
        }

        //shows the popup using bootstrap's modal plugin
        $element.modal({
            backdrop: 'static',
            show: true
        });

        // if there is a backdrop_border it means we're using a 'mini' backdrop
        // so remove the big backdrop that covers the whole screen
        if ($('.backdrop_border').length != 0) {
            $('.modal-backdrop').remove();
        }
    }
    else {
        //safe way to show popup when bootstrap plugin doesn't exist
        document.getElementById(idName).style.display = "block";

        if ($(".modal-backdrop").length == 0) {
            var backdrop = document.createElement('div');
            backdrop.id = idName + "_modal_backdrop";
            backdrop.classList.add('modal-backdrop');
            backdrop.classList.add('in');
            document.body.appendChild(backdrop); // have to remove on hide
        }
    }

    if (arguments.length === 2) {
        var offsetElement = arguments[1];
        var offset = $(offsetElement).offset();
        var topOffset = offset.top + $(offsetElement).height();
        var leftPadding = parseInt($element.css('padding-left').replace("px", ""), 10);
        var leftOffset = offset.left - leftPadding;
        $element.css({
            top: topOffset + "px",
            left: leftOffset + "px"
        });
    }

}

function hidePopup(idName) {
$ curl -s "https://structuredweb.dell.com/sw/app/CommonUI/JS/formHelper.js" 2>/dev/null | head -400

//note requires jQuery for isArray() support - or isArray must be polyfilled
//trySave disables elements given and runs a validation then a submit function if validation succeeds
//(such as disabling form submit buttons when save is pressed)
//if validation doesn't succeed then the elements given are re-enabled
//o is an array of elements or a single element (e.g. your save buttons)
//validate is the validation function which must return true or false
//submit is submit function (usually form submit, theoretically could do an ajax submit func here)
function trySave(o, validate, submit) {
    var elements;
    if (typeof validate !== "function" || typeof submit !== "function") {
        throw "validate and submit must be functions";
    }
    if (o === null) {
        throw "must supply element or array for first argument"
    }
    if (Array.isArray(o)) {
        elements = o;
    } else {
        elements = [o];
    }
    setElementsState(elements, false);
    if (validate()) {
        submit();
    } else {
        setElementsState(elements, true);
    }
}
//toggles elements disabled state
function setElementsState(elements, enabled) {
    for (var i = 0; i < elements.length; i++) {
        if (elements[i] !== null) {
            elements[i].disabled = !enabled;
        }
    }
}
$ curl -s "https://structuredweb.dell.com/sw/app/CommonUI/JS/resizeIFrame.js" 2>/dev/null

var getFFVersion = navigator.userAgent.substring(navigator.userAgent.indexOf("Firefox")).split("/")[1];
var FFextraHeight = parseFloat(getFFVersion) >= 0.1 ? 30 : 0;  //extra height in px to add to iframe in FireFox 1.0+ browsers

function resizeIframe(frameid) {
    var currentfr = document.getElementById(frameid);
    if (currentfr && !window.opera) {
        setupIframe(currentfr);
        currentfr.style.display = "block";
        var heightBefore = currentfr.height;
        var scrollHeight;
        var extra = 0;
        try {
            var frameDoc = null;
            var topBefore = window.document.documentElement.scrollTop;
            var scrollingBefore = currentfr.scrolling;
            currentfr.scrolling = 'no';
            currentfr.height = 10; //force it to recalculate, otherwise on location change the bigger size stays
            if (currentfr.Document && currentfr.Document.body.scrollHeight) //ie5+ syntax
            {
                frameDoc = currentfr.Document;
                if (scrollingBefore == 'auto' || scrollingBefore == 'yes') {
                    scrollHeight = frameDoc.body.scrollHeight;
                    extra = 30; //I added 30 pixels for auto scrolling
                }
                else {
                    scrollHeight = frameDoc.body.scrollHeight;
                }
                clientHeight = frameDoc.body.clientHeight;
            }
            else if (currentfr.contentDocument.body)//Firefox
            {

                frameDoc = currentfr.contentDocument;
                scrollHeight = frameDoc.body.scrollHeight;
                clientHeight = frameDoc.body.clientHeight;
                extra = FFextraHeight;
            }

            var absElements = findAbsoluteElements(frameDoc);
            var absBottom = bottomAbsoluteElements(absElements);
            scrollHeight = Math.max(scrollHeight, absBottom);
            
            currentfr.height = scrollHeight + extra;

            currentfr.scrolling = scrollingBefore;

            
            window.document.documentElement.scrollTop = topBefore;
        }
        catch (error) {
            currentfr.height = 800;
        }
    }
}
function setupIframe(iframeElement) {
    if (iframeElement.addEventListener) {
        iframeElement.addEventListener("load", readjustIframe, false);
    }
    else if (iframeElement.attachEvent) {
        iframeElement.detachEvent("onload", readjustIframe); // Bug fix line
        iframeElement.attachEvent("onload", readjustIframe);
    }
}
function readjustIframe(loadevt) {
	var crossevt = (window.event) ? event : loadevt;
	var iframeroot = (crossevt.currentTarget) ? crossevt.currentTarget : crossevt.srcElement;
	if (iframeroot)
		resizeIframe(iframeroot.id);
}

function resizeIframeWidth(frameid) {

	var frame = document.getElementById(frameid);
	var frameContent;
	var contentWidth;
	if (frame.Document && frame.Document.body.width) //ie5+ syntax
	{
		frameContent = frame.Document.body;
	}
	else if (frame.contentWindow.document.documentElement) {
		frameContent = frame.contentWindow.document.documentElement;
	}
	else if (frame.contentWindow.document.body) {
		frameContent = frame.contentWindow.document.body;
	}
	contentWidth = frameContent.scrollWidth;
	frame.width = contentWidth;
}

function findAbsoluteElements(doc) {
    var all = doc.getElementsByTagName("*");
	var absElements = new Array();
	for (var i = 0; i < all.length; i++) {
		if (all[i].position == 'absolute' || all[i].style.position == 'absolute') {
			absElements[absElements.length] = all[i];
		}
	}
	return absElements;
}

function bottomAbsoluteElements(absElements) {
	var bottom = 0;
	for (var i = 0; i < absElements.length; i++) {
		var elemBottom = absElements[i].offsetTop + absElements[i].offsetHeight;
		bottom = Math.max(bottom, elemBottom);
	}
	return bottom;
}

//new non-global dependent
function resizeCaller() {
    var iframes = document.getElementsByTagName("iframe");
    for (i = 0; i < iframes.length; i++) {
        if (document.getElementById && iframes[i].id) {
            resizeIframe(iframes[i].id);
        }
    }

    //Only continue for child windows, the top window is it's own parent 
    if (window.parent != window) {
        if (parent.resizeCaller) {
            parent.resizeCaller();
        }
    }
}

function recursiveResize(frame){
	if(typeof frame !== "undefined"){
		
		if(frame.parent && frame.top !== frame.self){
			recursiveResize(frame.parent);
		}
		if(frame.resizeCaller){
			setTimeout(frame.resizeCaller,700);
		}
	}
}
