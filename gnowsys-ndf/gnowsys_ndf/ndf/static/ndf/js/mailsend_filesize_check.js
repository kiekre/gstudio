$(document).ready(function(){
	$("#attached_files_id").change(function(){
		var f = document.getElementById("attached_files_id");
		var totalSize = 0;
		for(var i = 0; i<f.files.length ; ++i){
			totalSize += f.files[i].size
		}
		var limit = 1024*1024*25; // 25 MB
		if(totalSize > limit){
			document.getElementById("fileError").innerHTML = 'File size is greater than 25 MB';
			document.getElementById("send_mail").disabled = true;
		}
		else {
			document.getElementById("fileError").innerHTML = '';
			document.getElementById("send_mail").disabled = false;
		}
	});
});