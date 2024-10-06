import React, { useEffect, useState } from 'react'
import { useNavigate } from "react-router-dom";
import { Card, Button, Form, Input, message  } from 'antd'

//move it somewhere
function getCookie(key) {
    var b = document.cookie.match("(^|;)\\s*" + key + "\\s*=\\s*([^;]+)");
    return b ? b.pop() : null;
  }
  
  function getFromLocalStorage(key) {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;
  
      const parsedItem = JSON.parse(item);
      if (parsedItem.expiration && new Date().getTime() > parsedItem.expiration) {
        localStorage.removeItem(key);
        console.log("kuuuuutas");
      
        console.log(new Date().getTime(), parsedItem.expiration);
        console.log(`Item '${key}' wygasł i został usunięty z localStorage.`);
        return null;
      }
  
      return parsedItem.value;
    } catch (error) {
      console.error("Błąd podczas odczytu z localStorage:", error);
      return null;
    }
  }
const url = 'ws://localhost:8001/connect';
const LandingPage = () => {
    let navigate = useNavigate();
    useEffect(() => {
        // if (getFromLocalStorage("token") === null){
        //     return navigate("/login");
        // }
      }, [])

      const [form] = Form.useForm();
      const [messages, setMessages] = useState([]);
      const [socket, setSocket] = useState(null);
      const [inputMessage, setInputMessage] = useState('');
      const [posts, setPosts] = useState([[]])
      const [open, setOpen] = useState(false);
      const [confirmLoading, setConfirmLoading] = useState(false);
      const [modalText, setModalText] = useState('Content of the modal');
      const [newestPost, setNewestPost] = useState("2024-10-05 22:57:55.321049")
      const [counter, setCounter] = useState(0)
      const [messageApi, contextHolder] = message.useMessage();

      const showModal = () => {
        setOpen(true);
      };

      const handleOk = () => {
        setModalText('The modal will be closed after two seconds');
        setConfirmLoading(false);
        setOpen(false);
      };
    
      const handleCancel = () => {
        console.log('Clicked cancel button');
        setOpen(false);
      };
    
      useEffect(() => {
        // Tworzenie połączenia WebSocket
        const newSocket = new WebSocket(url);
    
        // Obsługa otwarcia połączenia
        newSocket.onopen = () => {
          console.log('WebSocket połączenie otwarte');
        };
    
        // Obsługa otrzymanych wiadomości
        newSocket.onmessage = (event) => {
          const message = JSON.parse(event.data);
          setNewestPost(message.body)
          setCounter((prevCount) => prevCount + 1)
        };
    
        // Obsługa błędów
        newSocket.onerror = (error) => {
          console.error('Błąd WebSocket:', error);
        };
    
        // Obsługa zamknięcia połączenia
        newSocket.onclose = () => {
          console.log('WebSocket połączenie zamknięte');
        };
    
        // Zapisanie socketu w stanie
        setSocket(newSocket);
    
        // Czyszczenie przy odmontowaniu komponentu
        return () => {
          newSocket.close();
        };
      }, [url]);
    
      // Funkcja do wysyłania wiadomości
      const sendMessage = (e) => {
        e.preventDefault();
        if (socket && socket.readyState === WebSocket.OPEN && inputMessage.trim() !== '') {
          socket.send(JSON.stringify({ message: inputMessage }));
          setInputMessage('');
        }
      };
    const request_posts = (time) => {
      fetch(`http://localhost:8001/todos/older_than/${time}`)
          .then((res) => {
            //console.log(newestPost);
            return res.json();
          })
          .then((data) => {
            setPosts((prevPosts) => [data.todos])
          });
        // Przykład użycia funkcji:
    }

    useEffect(() => {
      console.log(counter);
      if(counter==5){
        messageApi.open({
          type: 'warning',
          content: 'There are 5+ new posts on this topic refresh page to see them',
          duration: 1000,
        });
      }
    }, [counter])
    

    useEffect(() => {
      var date = new Date();
      request_posts(`${date.getUTCFullYear()}-${date.getUTCMonth() + 1}-${date.getUTCDate()} ${date.getUTCHours()}:${date.getUTCMinutes()}:${date.getUTCSeconds()}.599999`)
      }, []);

    function handle_posts_request(value) {
        postData(`http://localhost:8000/posts?title=${value.author}&description=${value.text}`)
        .then(data => {
            console.log(data.details); // Loguj odpowiedź z serwera
            let modifiedString = data.details.body.toString();
            modifiedString = modifiedString.slice(0, -1) + '9';
            request_posts(modifiedString);
            
            // Ustawianie wartości pól na puste
            form.setFieldValue('text', "");
            form.setFieldValue('author', "");
            setCounter(0);
        })

        .catch(error => {
            console.error('Błąd:', error); // Obsługa błędów
        });
    }
    const { TextArea } = Input;
    useEffect(() => {
        console.log(posts);
      }, [posts])
      
      async function postData(url = '', data = {}) {
        // Domyślne ustawienia dla metody POST
        const response = await fetch(url, {
          method: 'POST', // Metoda HTTP
          headers: {
            'Content-Type': 'application/json' // Typ zawartości, dane wysyłane w formacie JSON
          },
          body: JSON.stringify(data) // Konwersja danych do formatu JSON
        });
      
        // Zwraca odpowiedź jako obiekt JSON
        return response.json(); 
      }
      
      
    
      return (
        <>
        {contextHolder}
        <div className='flex flex-col items-center  w-screen h-screen overflow-auto'>
          <ul className='mt-10'>
          <Card className="flex justify-center space-y-4 mr-5" style={{
              width: 630,
              height: 290,
              margin: "10px",
              borderRadius: "20px",
              overflow: "hidden",
            }}>
            <Form
                layout={'horizontal'}
                form={form}
                variant={'filled'}
                initialValues={{ layout: 'horizontal' }}
                onFinish={handle_posts_request}
                >
                <Form.Item name={"text"} required={true}>
                <TextArea rows={4} placeholder="Text" />
                </Form.Item>
                <Form.Item name={"author"} required={true}>
                    <Input style={{height: '45px', width: '550px'}} placeholder="Author" />
                </Form.Item>
                <Form.Item style={{ marginBottom: "16px"}} className='flex items-center justify-center'>
                    <Button htmlType="submit"  style={{
                            width: '171px',
                            height: '46px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            fontWeight: 'bold',
                            backgroundImage: "linear-gradient(to right, #80A1D4, #75C9C8)",
                             }} type="primary">Post
                    </Button>
                </Form.Item>
                
            </Form>
          </Card>
          <div key={newestPost}> 
            {posts[0].map((message, index) => (
                <li key={index}> <Card className="flex space-y-2" style={{
                  width: 630,
                  height: 236,
                  margin: "10px",
                  borderRadius: "20px",
                  overflow: "hidden",
              }}><h2 className='font-bold text-2xl'>{message.title}</h2>
                <p className='overflow-auto'>{message.description}</p>
              </Card></li>
              ))}
          </div>
          </ul>
        </div>
        </>
      );
    };

export default LandingPage