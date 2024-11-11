import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Card, Button, Form, Input, message, Upload, Image } from 'antd';
import { UploadOutlined } from '@ant-design/icons';


const ProfileEdit = () => {
    let navigate = useNavigate();
    const [form] = Form.useForm();
    const [messageApi, contextHolder] = message.useMessage();
    const { TextArea } = Input;



    return (
        <>
            {contextHolder}
            <div className='flex flex-col items-center overflow-auto'>
                <ul className='mt-10'>
                    <Card 
                        className="flex justify-center space-y-4 mr-5" 
                        style={{
                            width: 630,
                            height: 'auto',
                            margin: "10px",
                            borderRadius: "20px",
                            overflow: "hidden",
                            backgroundColor: ""
                        }}
                    >
                        <Form
                            layout={'horizontal'}
                            form={form}
                            variant={'filled'}
                            initialValues={{ layout: 'horizontal' }}
                            //onFinish={handle_posts_request}
                        >
                            <Form.Item 
                                name="title" 
                                rules={[{ required: true, message: 'Please input the title!' }]}
                            >
                                <Input style={{height: '45px'}} placeholder="Title" />
                            </Form.Item>
                            
                            <Form.Item 
                                name="description" 
                                rules={[{ required: true, message: 'Please input the description!' }]}
                            >
                                <TextArea rows={4} placeholder="Description" />
                            </Form.Item>
                            
                            <Form.Item 
                                name="author" 
                                rules={[{ required: true, message: 'Please input the author!' }]}
                            >
                                <Input style={{height: '45px'}} placeholder="Author" />
                            </Form.Item>
                            
                            <Form.Item 
                                name="community"
                            >
                                <Input style={{height: '45px'}} placeholder="Community (optional)" />
                            </Form.Item>

                            <Form.Item className='flex items-center justify-center'>
                                <Button 
                                    htmlType="submit"  
                                    style={{
                                        width: '171px',
                                        height: '46px',
                                        borderRadius: "100px",
                                        fontWeight: 'bold',
                                        backgroundImage: "linear-gradient(to right, #80A1D4, #75C9C8)",
                                    }} 
                                    type="primary"
                                >
                                    Post
                                </Button>
                            </Form.Item>
                        </Form>
                    </Card>
                </ul>
            </div>
        </>
    );
};

export default ProfileEdit;