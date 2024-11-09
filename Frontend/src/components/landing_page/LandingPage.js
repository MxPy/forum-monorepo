import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Card, Button, Form, Input, message, Upload, Image } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const url = 'ws://localhost:8001/connect';

const LandingPage = () => {
    let navigate = useNavigate();
    const [form] = Form.useForm();
    const [socket, setSocket] = useState(null);
    const [posts, setPosts] = useState([]);
    const [newestPost, setNewestPost] = useState("2024-10-05 22:57:55.321049")
    const [counter, setCounter] = useState(0)
    const [messageApi, contextHolder] = message.useMessage();
    const { TextArea } = Input;

    // ... WebSocket setup code remains the same ...

    const request_posts = async (time) => {
        try {
            const response = await fetch(`http://localhost:8001/todos/older_than/${time}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            setPosts(data.todos || []);
        } catch (error) {
            console.error('Error fetching posts:', error);
            messageApi.error('Failed to fetch posts');
        }
    };

    useEffect(() => {
        if(counter === 5){
            messageApi.open({
                type: 'warning',
                content: 'There are 5+ new posts on this topic refresh page to see them',
                duration: 1000,
            });
        }
    }, [counter, messageApi]);

    useEffect(() => {
        const date = new Date();
        const formattedDate = `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}-${date.getUTCDate()} ${date.getUTCHours()}:${date.getUTCMinutes()}:${date.getUTCSeconds()}.599999`;
        request_posts(formattedDate);
    }, []);

    const normFile = (e) => {
        if (Array.isArray(e)) {
            return e;
        }
        return e?.fileList;
    };

    async function handle_posts_request(values) {
        const formData = new FormData();
        formData.append('title', values.title);
        formData.append('description', values.description);
        formData.append('author', values.author);
        formData.append('community', values.community || 'default');
        
        if (values.file?.[0]?.originFileObj) {
            formData.append('file', values.file[0].originFileObj);
        }

        try {
            const response = await fetch('http://localhost:8000/posts', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.details?.body?.created_at) {
              console.log("jusdsdsd");
              const date = new Date();
                await request_posts(`${date.getUTCFullYear()}-${date.getUTCMonth() + 1}-${date.getUTCDate()} ${date.getUTCHours()}:${date.getUTCMinutes()}:${date.getUTCSeconds()}.599999`);
                form.resetFields();
                setCounter(0);
                messageApi.success('Post created successfully!');
            } else {
                // Handle case where response is success but missing expected data
                console.warn('Unexpected response structure:', data);
                messageApi.warning('Post created but refresh may be needed');
            }
        } catch (error) {
            console.error('Error:', error);
            messageApi.error('Error creating post: ' + error.message);
        }
    }

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
                            onFinish={handle_posts_request}
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
                            
                            <Form.Item 
                                name="file"
                                valuePropName="fileList"
                                getValueFromEvent={normFile}
                            >
                                <Upload 
                                    maxCount={1}
                                    beforeUpload={() => false}
                                    listType="picture"
                                >
                                    <Button icon={<UploadOutlined />}>Upload Image</Button>
                                </Upload>
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

                    <div key={newestPost}> 
                        {posts.map((post, index) => (
                            <li key={index}>
                                <Card
                                    className="flex flex-col space-y-2"
                                    style={{
                                        width: 640,
                                        height: 'auto',
                                        margin: "10px",
                                        borderRadius: "20px",
                                        borderColor: "#0d0221",
                                        overflow: "hidden",
                                        backgroundColor: "#001529",
                                        position: "relative"
                                    }}
                                >
                                    <div className="relative z-10 flex flex-col space-y-2 p-4">
                                        <h2 className='font-bold text-2xl text-gray-300'>{post.title}</h2>
                                        <p className='text-gray-600'>Posted by {post.author} in {post.community}</p>
                                        <p className='overflow-auto text-gray-300'>{post.description}</p>
                                    </div>

                                    {/* Kontener na media z efektem bluru ograniczonym do tego obszaru */}
                                    <div className='relative flex justify-center items-center w-full' 
                                        style={{ minHeight: '300px' }}>
                                        
                                        {/* Warstwa z blurem - ograniczona do obszaru media */}
                                        <div
                                            className='absolute top-0 left-0 w-full h-full'
                                            style={{
                                                backgroundImage: `url(${post.imageLink})`,
                                                backgroundSize: 'cover',
                                                backgroundPosition: 'center',
                                                filter: 'blur(20px)',
                                                opacity: '0.3',
                                                transform: 'scale(1.1)',
                                                zIndex: 0
                                            }}
                                        />

                                        {/* Treść media z wyższym z-index */}
                                        <div className="relative z-10">
                                            {post.imageLink.includes("mp4") ? (
                                                <video
                                                    controls
                                                    className='max-h-[600px] w-auto object-contain'
                                                    style={{ maxWidth: '100%' }}
                                                >
                                                    <source src={post.imageLink} type="video/mp4"/>
                                                </video>
                                            ) : (
                                                <Image
                                                    src={post.imageLink}
                                                    alt="Post image"
                                                    className="max-h-[600px] w-auto object-contain"
                                                    style={{ maxWidth: '100%' }}
                                                    onError={(e) => {
                                                        console.error('Image loading error:', e);
                                                        e.target.style.display = 'none';
                                                    }}
                                                />
                                            )}
                                        </div>
                                    </div>

                                    <p className='text-sm text-gray-500 mt-2 px-4'>
                                        Votes: {post.vote_count}
                                    </p>
                                </Card>
                            </li>
                        ))}
                    </div>
                </ul>
            </div>
        </>
    );
};

export default LandingPage;