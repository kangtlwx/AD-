# PS1脚本内容
ad用户密码到期，邮件通知
Import-Module Activedirectory
$allUsers = Get-ADUser -SearchBase "OU=Arizonrfid,DC=arizonrfid,DC=com" -SearchScope Subtree -Filter {Enabled -eq $True -and PasswordNeverExpires -eq $False} -Properties DisplayName,PasswordExpired,mail,CannotChangePassword,"msDS-UserPasswordExpiryTimeComputed" | Where-Object {$_.DisplayName -ne $null -and $_.PasswordExpired -eq $False -and $_.CannotChangePassword -eq $False -and $_.mail -ne $null -and $_.DistinguishedName -notlike "*OU=台湾永道,OU=Arizonrfid,DC=arizonrfid,DC=com" -and $_.DistinguishedName -notlike "*OU=总经理室,OU=Arizonrfid,DC=arizonrfid,DC=com" -and $_.DistinguishedName -notlike "*OU=日本永道,OU=Arizonrfid,DC=arizonrfid,DC=com"}
$passExpiresUsersList = @()
$nowTime = Get-Date
 
foreach ($user in $allUsers){
$ExpiryDate = [datetime]::FromFileTime($user."msDS-UserPasswordExpiryTimeComputed")
$expire_days = ($ExpiryDate - $nowTime).Days
 

if($expire_days -lt 15 -and $expire_days -gt -1 ){
$displayname= $user.Displayname

$email=
"Dear $displayname :
 
您的邮箱密码即将在 $expire_days 天后过期，密码过期之后您将无法登陆邮箱系统，请您尽快更改。
密码更改方式：
您可访问资讯综合自助平台（http://10.10.65.218），并点击-[邮箱密码修改]，详细步骤可以点击-[下载SOP]，按照SOP操作即可。
如遇密码相关问题，请随时联系资讯部。

AD地址:10.10.65.6
需求说明：
1、建立密码提醒group，名称是Pw-change-remind，并添加对应domain-group和user。部分永不过期的用户，是否可以实现邮件不提醒。
2、提醒时间为过期前15/7/3/1天。
3、提醒发信人为arizonrfid@abc.com

"
 
Send-MailMessage -From "arizonrfid@abc.com" -To $user.mail -Subject "您的邮箱密码即将过期" -Body $email -SmtpServer ex.abc.com -Encoding ([System.Text.Encoding]::UTF8)
 

$userobject=New-object psobject
$userobject | Add-Member -membertype noteproperty -Name 用户名 -value $user.SamAccountName
$userobject | Add-Member -membertype noteproperty -Name 邮箱 -Value $user.mail
$userobject | Add-Member -membertype noteproperty -Name 密码过期时间 -Value $ExpiryDate
$userobject | Add-Member -membertype noteproperty -Name 剩余密码过期天数 -Value $expire_days
$passExpiresUsersList+=$userobject
}
}

$EmailbodyHTML = $passExpiresUsersList | sort-object 剩余密码过期天数 | ConvertTo-Html | Out-String
Send-Mailmessage -From  "arizonrfid@abc.com" –To “it_support@abc.com；” -BodyAsHtml $EmailbodyHTML -Subject "管理员通知" -SmtpServer ex.abc.com -Encoding ([System.Text.Encoding]::UTF8)
