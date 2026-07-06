<?php
// Replace with your email address
$receiving_email_address = "your@email.com";

// Check if form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {

  $name = htmlspecialchars($_POST['name']);
  $email = htmlspecialchars($_POST['email']);
  $subject = htmlspecialchars($_POST['subject']);
  $message = htmlspecialchars($_POST['message']);

  // Email content
  $email_subject = "New Contact Form Message: " . $subject;
  
  $email_body = "You have received a new message from your website contact form.\n\n".
                "Name: $name\n".
                "Email: $email\n".
                "Subject: $subject\n\n".
                "Message:\n$message\n";

  // Email headers
  $headers = "From: $name <$email>\r\n";
  $headers .= "Reply-To: $email\r\n";
  $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

  // Send email
  if(mail($receiving_email_address, $email_subject, $email_body, $headers)){
    echo "OK";
  } else {
    echo "Message could not be sent.";
  }

} else {
  echo "Invalid request.";
}
?>