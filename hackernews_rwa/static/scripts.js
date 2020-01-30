$(document).ready(function(){
	$('.menu-toggle').on('click', function(){
		$('.nav').toggleClass('showing');
		$('.nav ul').toggleClass('showing');
	});
});


$(function(){
	$("#header").load("header.html");
});