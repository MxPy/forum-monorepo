import React, { useState, useEffect } from 'react'
import { Card } from 'antd'
import { Button, Form, Input, Switch } from 'antd';
import {ReactComponent as Languages} from '../../assets/Languages.svg';
import { useNavigate } from "react-router-dom";


const Login = () => {
  const [form] = Form.useForm();
  const [loginOrRegister, setloginOrRegister] = useState(true)
  const [showRessetPasswordModal, setshowRessetPasswordModal] = useState(false)
  const [passwordCode, setpasswordCode] = useState("0000")
  let navigate = useNavigate();

  function handle_register() {
    setloginOrRegister(!loginOrRegister)
  }

  function handle_proceed() {
    setshowRessetPasswordModal(false)
    setloginOrRegister(true)
  }


  function setCookie(key, value, expirationDate) {
    try {
      let cookieString = `${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
      
      if (expirationDate) {
        const date = new Date(expirationDate);
        if (isNaN(date.getTime())) {
          throw new Error("wrong date");
        }
        cookieString += `; expires=${date.toUTCString()}`;
      }
      
      cookieString += "; path=/";
      
      document.cookie = cookieString;
  
    } catch (error) {
      console.error("cookie set error: ", error);
    }
  }

  //we use it cause cookies are blocked in http connection by default in prod use setcookie
  function setLocalStorage(key, value, expirationDate) {
    try {
      const item = {
        value: value,
        expiration: expirationDate ? new Date(expirationDate).getTime()+ (2*60*60*1000) : null
      };

      localStorage.setItem(key, JSON.stringify(item));
  
    } catch (error) {
      console.error("Błąd podczas zapisu do localStorage:", error);
    }
  }

  function getFromLocalStorage(key) {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;
      
      
      const parsedItem = JSON.parse(item);
      if (parsedItem.expiration && new Date().getTime() > parsedItem.expiration) {
        localStorage.removeItem(key);
        console.log(`Item '${key}' wygasł i został usunięty z localStorage.`);
        return null;
      }
  
      return parsedItem.value;
    } catch (error) {
      console.error("Błąd podczas odczytu z localStorage:", error);
      return null;
    }
  }

  useEffect(() => {
    if (getFromLocalStorage("token") !== null){
        return navigate("/");
    }
  }, [])



  useEffect(() => {
    console.log(showRessetPasswordModal)
  
  }, [])
  

  function handle_language() {
    return navigate("/language");
  }
  return (
    <div className='flex flex-col items-center justify-center w-screen h-screen'>
        <Card className="flex justify-center space-y-4" style={{
              width: 330,
              height: 436,
              margin: "20px",
              borderRadius: "20px",
              overflow: "hidden",
        }}>
            {loginOrRegister ? (<>
                <div className='flex justify-center pb-6 pt-4'>
                <h1 className='text-3xl font-semibold text-[#446FB1]'>Login</h1>
            </div>
            <Form
                layout={'horizontal'}
                form={form}
                variant={'filled'}
                initialValues={{ layout: 'horizontal' }}
                //onFinish={handle_login_request}
                >
                <Form.Item name={"username"} required={true}>
                    <Input style={{height: '45px', width: '257px'}} placeholder="Username" />
                </Form.Item>
                <Form.Item name={"password"} required={true}>
                    <Input.Password style={{height: '45px', width: '257px'}} placeholder="Password" />
                </Form.Item>
                <Form.Item style={{ marginBottom: "37px" }} valuePropName="checked">
                    <div className='flow-root '>
                        <p className='float-left pl-4 text-[#446FB1]'>Remeber Me</p>
                        <div className='pr-4 float-right'>
                            <Switch />
                        </div>
                    </div>
                </Form.Item>
                <Form.Item style={{ marginBottom: "16px"}} className='flex items-center justify-center'>
                    <Button htmlType="submit"  style={{
                            width: '171px',
                            height: '46px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            fontWeight: 'bold',
                            backgroundImage: "linear-gradient(to right, #80A1D4, #75C9C8)",
                             }} type="primary">Login
                    </Button>
                </Form.Item>
                
            </Form>
            <div className='flow-root '>
                        <div className='float-left  '><Button style={{
                            width: '120px',
                            height: '30px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            border: 'solid',
                            fontWeight: 'bold',
                            borderColor: "#80A1D4",
                            color:"#80A1D4",
                             }} 
                             onClick={handle_register}
                             type="link">
                            <div>
                              Register
                            </div>
                    </Button></div>
                        <div className=' float-right'>
                        <Button style={{
                            width: '125px',
                            height: '30px',
                            borderRadius: "100px",
                            overflow: "hidden",
                            border: 'solid',
                            fontWeight: 'bold',
                            borderColor: "#80A1D4",
                            color:"#80A1D4",
                             }} 
                             onClick={handle_register}
                             type="link">
                            <div>
                            Forgot Password
                            </div>
                    </Button>
                        </div>
                    </div>
            </>) : (<>{showRessetPasswordModal ? (<>
                    <h1 className='text-3xl text-center font-bold text-[#ff3636] pb-6'>Register</h1>
                    <p className='text-xl text-center pb-10'>
                    The following code is used to reset your password, save it in a safe place as you will not receive it a second time
                    </p>
                    <p className='text-5xl font-bold text-center pb-12'>
                        {passwordCode}
                    </p>
                    <div className='flex items-center justify-center'>
                        <Button onClick={handle_proceed} style={{
                                width: '200px',
                                height: '60px',
                                borderRadius: "100px",
                                overflow: "hidden",
                                backgroundImage: "linear-gradient(to right, #80A1D4, #75C9C8)",
                                }} type="primary">Proceed
                        </Button>
                    </div>
                    
                </> ):(<>
                    <div className='flex justify-center pb-6 pt-4'>
                    <h1 className='text-3xl font-semibold text-[#446FB1]'>Register</h1>
                    </div>
                    <Form
                        layout={'horizontal'}
                        form={form}
                        variant={'filled'}
                        initialValues={{ layout: 'horizontal' }}
                        //onFinish={handle_register_request}
                        >
                        <Form.Item name={"username"} required={true}>
                            <Input style={{height: '45px', width: '257px'}} placeholder="Username" />
                        </Form.Item>
                        <Form.Item name={"password"} required={true}>
                            <Input.Password style={{height: '45px', width: '257px'}} placeholder="Password" />
                        </Form.Item>
                        <Form.Item name={"password2"} required={true}>
                            <Input.Password style={{height: '45px', width: '257px'}} placeholder="Repeat Password" />
                        </Form.Item>
                        <Form.Item style={{ marginBottom: "16px"}} className='flex items-center justify-center'>
                            <Button htmlType="submit" style={{
                                    width: '171px',
                                    height: '46px',
                                    borderRadius: "100px",
                                    overflow: "hidden",
                                    fontWeight: 'bold',
                                    backgroundImage: "linear-gradient(to right, #80A1D4, #75C9C8)",
                                    }} type="primary">Register
                                    
                            </Button>
                        </Form.Item>
                        
                    </Form>
                    <div className='flex items-center justify-center pb-20'>
                            <Button  style={{
                                   width: '125px',
                                   height: '30px',
                                   borderRadius: "100px",
                                   overflow: "hidden",
                                   border: 'solid',
                                   fontWeight: 'bold',
                                   borderColor: "#80A1D4",
                                   color:"#80A1D4",
                                    }} 
                                    onClick={handle_register}
                                    type="link">
                                    Login
                            </Button>
                    </div>
                        
                </> )}
                
            </>) }
            
        </Card>
        
        <Button color="default" variant="link" disabled={showRessetPasswordModal} onClick={handle_language}>
            <Languages/>
            <p className='float-left pl-4 text-white font-semibold'>Change Language</p>          
        </Button>
        
    </div>
  )
}

export default Login