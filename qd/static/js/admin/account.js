$(function () {
  var $select_user = $('#edit-account select[name=user]').selectize({
  })
  var select_user = $select_user[0].selectize;

  var $select_exchange = $('#edit-account select[name=exchange]').selectize({
  })
  var select_exchange = $select_exchange[0].selectize;

  // 删除账号
  $('body').on('click', '[name=delete]', function (e) {
    var tds = $(this).parent().parent().children();
    var user = $(tds[0]).data('user');
    var duser = $(tds[0]).text();
    var exchange = $(tds[1]).text();
    var login_name = $(tds[2]).text();
    if (confirm('确实要删除账号<' + duser + '/' + exchange 
        + '/' + login_name + '>的资料吗? 删除操作不可撤销')) {
      $.post(
        url_delete_account,
        {user: user,
         exchange: exchange,
         login_name: login_name},
        ajax_refresh);
    }
  })

  // 编辑账号
  $('body').on('click', '[name=edit]', function (e) {
    var tds = $(this).parent().parent().children();
    var user = $(tds[0]).data('user');
    var exchange = $(tds[1]).text();
    var login_name = $(tds[2]).text();
    select_user.setValue(user);
    select_exchange.setValue(exchange);
    $('#edit-account input[name=login_name]').val(login_name);
    $('a[href="#edit-account"]').tab('show');
    $('#edit-account input[name=login_password]').focus();
  })

  // 保存
  $('body').on('click', '[name=upsert]', function (e) {
    var params = {
      user: $('#edit-account select[name=user]').val(),
      exchange: $('#edit-account select[name=exchange]').val(),
      login_name: $('#edit-account [name=login_name]').val(),
      login_password: $('#edit-account [name=login_password]').val(),
      money_password: $('#edit-account [name=money_password]').val(),
      bank_password: $('#edit-account [name=bank_password]').val(),
    };
    console.log(params);
    if (!params.user || !params.exchange 
        || !params.login_name || !params.login_password) {
      alert('用户/交易所/交易账号/交易密码都不能为空');
    } else {
      $.post(
        url_upsert_account,
        params,
        ajax_refresh);
    }
  })

  // 导入账号
  $('body').on('click', 'button[name=import]', function (e) {
    var text = $('textarea[name=import]').val();
    $.post(
        url_import_account,
        {text: text},
        ajax_refresh);
  })
});
